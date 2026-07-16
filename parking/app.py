import streamlit as st
import pandas as pd
import folium
import plotly.express as px
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster

st.set_page_config(
    page_title="서울시 공영주차장",
    page_icon="🅿",
    layout="wide"
)

st.title("🅿 서울시 공영주차장 정보")

#####################################
# CSV 업로드
#####################################
uploaded_file = st.sidebar.file_uploader("CSV 업로드", type=["csv"])
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, encoding="utf-8")
else:
    try:
        df = pd.read_csv("parking.csv", encoding="utf-8")
    except FileNotFoundError:
        st.error("🚨 'parking.csv' 파일을 찾을 수 없습니다. CSV 파일을 업로드해주세요!")
        st.stop()

#####################################
# 컬럼명 확인
#####################################
st.sidebar.subheader("데이터")
st.sidebar.write(f"전체 주차장 수 : {len(df)}")

#####################################
# 주소 컬럼 찾기
#####################################
address_col = None
for c in df.columns:
    if "주소" in c:
        address_col = c
        break

#####################################
# 자치구 만들기
#####################################
if address_col:
    df["자치구"] = df[address_col].str.extract(r"서울특별시\s*(\S+)")
else:
    st.error("주소 컬럼이 없습니다.")
    st.stop()

#####################################
# 자치구 선택
#####################################
district = st.sidebar.selectbox(
    "자치구",
    ["전체"] + sorted(df["자치구"].dropna().unique().tolist())
)
if district != "전체":
    df = df[df["자치구"] == district]

#####################################
# 주소검색
#####################################
search = st.sidebar.text_input("주소 검색")
if search:
    df = df[df[address_col].str.contains(search, na=False)]

#####################################
# 무료 여부
#####################################
free_col = None
for c in df.columns:
    if "무료" in c:
        free_col = c
        break

if free_col:
    only_free = st.sidebar.checkbox("무료만 보기")
    if only_free:
        df = df[df[free_col].astype(str).str.contains("무료|Y|예")]

#####################################
# 운영시간
#####################################
time_col = None
for c in df.columns:
    if "운영" in c:
        time_col = c
        break

if time_col:
    only24 = st.sidebar.checkbox("24시간")
    if only24:
        df = df[df[time_col].astype(str).str.contains("24")]

#####################################
# 요금 필터링
#####################################
fee_col = None
for c in df.columns:
    if "기본요금" in c:
        fee_col = c
        break

if fee_col:
    # 안전하게 결측치 및 문자열을 숫자로 전처리
    df[fee_col] = df[fee_col].fillna("0").astype(str)
    # 숫자 형태만 추출하고, 추출되지 않은 행은 '0'으로 채우기
    df[fee_col] = df[fee_col].str.replace(",", "").str.extract(r"(\d+)").fillna(0).astype(int)
    
    # 데이터가 비어있지 않을 때만 슬라이더를 띄웁니다.
    if not df.empty:
        max_fee = int(df[fee_col].max())
        max_fee = max(max_fee, 1) # 에러 방지
        fee = st.sidebar.slider("기본요금", 0, max_fee, max_fee)
        df = df[df[fee_col] <= fee]
    else:
        st.sidebar.warning("조건에 맞는 요금 데이터가 없습니다.")

#####################################
# 가장 싼 주차장 정보 출력
#####################################
if fee_col and not df.empty:
    cheapest = df.sort_values(fee_col).head(1)
    if len(cheapest):
        st.success("🥇 조건 내 가장 저렴한 주차장")
        col1, col2, col3 = st.columns(3)
        col1.write(f"**이름**: {cheapest.iloc[0].iloc[0]}")
        col2.write(f"**주소**: {cheapest.iloc[0][address_col]}")
        col3.write(f"**기본요금**: {cheapest.iloc[0][fee_col]} 원")

#####################################
# 지도 시각화
#####################################
lat_col = None
lng_col = None
for c in df.columns:
    if "위도" in c:
        lat_col = c
    if "경도" in c:
        lng_col = c

if lat_col and lng_col:
    # 필터 결과 데이터가 없을 경우 에러 방지 (서울시청 기준)
    if not df.empty and df[lat_col].notna().any():
        center = [df[lat_col].mean(), df[lng_col].mean()]
        zoom = 11
    else:
        center = [37.5665, 126.9780]  # 서울시청 좌표
        zoom = 10
        st.warning("⚠️ 필터 결과와 일치하는 주차장 데이터가 없습니다.")

    m = folium.Map(location=center, zoom_start=zoom)
    cluster = MarkerCluster().add_to(m)

    # 지도 마커 생성
    if not df.empty:
        for _, row in df.iterrows():
            try:
                lat = float(row[lat_col])
                lon = float(row[lng_col])
                if pd.isna(lat) or pd.isna(lon):
                    continue
            except:
                continue

            parking_name = str(row.iloc[0])
            address = str(row[address_col]) if address_col else ""
            fee = str(row[fee_col]) if fee_col else "-"
            free = str(row[free_col]) if free_col else "-"
            operating = str(row[time_col]) if time_col else "-"

            # 마커 색상 조건 설정
            color = "blue"
            if free_col and ("무료" in free or "Y" in free or "예" in free):
                color = "green"
            elif fee_col:
                try:
                    if int(fee) >= 500:
                        color = "red"
                    elif int(fee) >= 300:
                        color = "orange"
                except:
                    pass

            popup = f"""
            <b>{parking_name}</b><br>
            주소 : {address}<br>
            기본요금 : {fee}원<br>
            무료 : {free}<br>
            운영 : {operating}
            """
            tooltip = f"{parking_name} ({fee}원)"

            folium.Marker(
                location=[lat, lon],
                popup=popup,
                tooltip=tooltip,
                icon=folium.Icon(color=color, icon="info-sign")
            ).add_to(cluster)

    st_folium(m, width=1200, height=600)
else:
    st.warning("위도·경도 컬럼이 없습니다.")

#####################################
# 통계
#####################################
st.divider()
st.subheader("📊 통계")
c1, c2, c3 = st.columns(3)
c1.metric("검색된 주차장 수", len(df))

if fee_col:
    avg_fee = int(df[fee_col].mean()) if not df.empty else 0
    c2.metric("평균요금", f"{avg_fee} 원")

if free_col:
    if not df.empty:
        free_cnt = len(df[df[free_col].astype(str).str.contains("무료|Y|예")])
    else:
        free_cnt = 0
    c3.metric("무료 주차장", free_cnt)

#####################################
# 자치구별 개수 차트
#####################################
if "자치구" in df.columns and not df.empty:
    chart = df.groupby("자치구").size().reset_index(name="주차장수")
    fig = px.bar(chart, x="자치구", y="주차장수", title="자치구별 공영주차장 수")
    st.plotly_chart(fig, use_container_width=True)

#####################################
# 평균 요금 차트
#####################################
if fee_col and not df.empty:
    fee_chart = df.groupby("자치구")[fee_col].mean().reset_index()
    fig2 = px.bar(fee_chart, x="자치구", y=fee_col, title="자치구별 평균 기본요금")
    st.plotly_chart(fig2, use_container_width=True)

#####################################
# 데이터 보기
#####################################
st.subheader("📋 주차장 목록")
st.dataframe(df, use_container_width=True, height=500)

#####################################
# CSV 다운로드
#####################################
if not df.empty:
    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button("📥 필터 결과 다운로드", csv, file_name="parking_result.csv", mime="text/csv")
