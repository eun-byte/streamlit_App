import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import random

# ==========================================
# 1. 페이지 초기 설정 및 통합 CSS 적용
# ==========================================
st.set_page_config(
    page_title="Eco Diary : 탄소발자국 탐정",
    page_icon="🌱",
    layout="wide"
)

# Python 내부에 CSS 구문을 st.markdown() 문자열로 안전하게 삽입
st.markdown("""
<style>
.main {
    background-color: #F4F9F4;
}

/* 카드 UI 스타일링 */
.metric-card {
    background-color: #FFFFFF;
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    border: 1px solid #E2E8F0;
    text-align: center;
    margin-bottom: 15px;
}

/* 지구 편지 스타일ing */
.earth-letter {
    background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%);
    border-left: 6px solid #2ECC71;
    border-radius: 12px;
    padding: 20px;
    font-size: 1.05rem;
    line-height: 1.6;
    color: #1B4332;
    margin-top: 15px;
}

/* 배지 스타일ing */
.badge-box {
    display: inline-block;
    background-color: #FFF9C4;
    border: 1px solid #FBC02D;
    border-radius: 20px;
    padding: 6px 14px;
    margin: 4px;
    font-weight: bold;
    color: #F57F17;
    font-size: 0.9rem;
}
</style>
""", unsafe_allow_html=True)  # <-- unsafe_allow_html 로 수정!


# ==========================================
# 2. 로직 함수 정의 (탄소 계산 및 지구 편지)
# ==========================================

EMISSION_FACTORS = {
    "transport": {
        "도보": 0.0,
        "자전거": 0.0,
        "버스": 1.2,
        "지하철": 0.8,
        "자동차": 5.5,
        "오토바이": 2.5
    },
    "meal": {
        "채식": 1.5,
        "일반식": 2.5,
        "육류 위주 식사": 4.8
    },
    "electricity_per_hour": 0.21,
    "shower_per_min": 0.12,
    "disposable_per_item": 0.05
}

AVERAGE_DAILY_EMISSION = 10.0

def calculate_emissions(transport, meal, electricity_hours, shower_mins, disposables, recycling, tumbler, green_actions):
    """카테고리별 탄소 배출량을 계산합니다."""
    e_transport = EMISSION_FACTORS["transport"].get(transport, 0.0)
    e_meal = EMISSION_FACTORS["meal"].get(meal, 2.5)
    e_elec = electricity_hours * EMISSION_FACTORS["electricity_per_hour"]
    e_shower = shower_mins * EMISSION_FACTORS["shower_per_min"]
    e_disp = disposables * EMISSION_FACTORS["disposable_per_item"]
    
    total_emission = e_transport + e_meal + e_elec + e_shower + e_disp
    
    reduction = 0.0
    if recycling: reduction += 0.3
    if tumbler: reduction += 0.2
    reduction += len(green_actions) * 0.15
    
    final_emission = max(0.1, round(total_emission - reduction, 2))
    
    breakdown = {
        "이동수단": round(e_transport, 2),
        "식사": round(e_meal, 2),
        "전기사용": round(e_elec, 2),
        "샤워": round(e_shower, 2),
        "일회용품": round(e_disp, 2)
    }
    
    return final_emission, breakdown

def calculate_eco_score(total_emission, recycling, tumbler, green_actions):
    """친환경 점수(100점 만점)를 산정합니다."""
    base_score = max(0, 70 - (total_emission / AVERAGE_DAILY_EMISSION) * 40)
    bonus = 0
    if recycling: bonus += 8
    if tumbler: bonus += 7
    bonus += min(15, len(green_actions) * 3)
    
    return int(min(100, base_score + bonus))

def get_earth_status(score):
    """점수에 맞는 지구 이모지 상태를 반환합니다."""
    if score >= 85: return "매우 행복", "😀"
    elif score >= 70: return "행복", "🙂"
    elif score >= 50: return "보통", "😐"
    elif score >= 35: return "슬픔", "😢"
    else: return "위험", "😭"

def generate_earth_letter(transport, meal, disposables, recycling, tumbler, green_actions, score):
    """입력값 기반으로 지구 편지를 동적 생성합니다."""
    praise_list = []
    regret_list = []
    
    if transport in ["도보", "자전거"]:
        praise_list.append(f"네가 **{transport}**를 타고 바람을 가를 때 내 몸도 시원해지는 느낌이었어!")
    elif transport in ["버스", "지하철"]:
        praise_list.append(f"**{transport}**을 타고 이동해 줘서 공기가 한결 맑아졌단다.")
        
    if meal == "채식":
        praise_list.append("맛있는 **채식**으로 식사해 줘서 고마워. 마음까지 가벼워졌어!")
    if tumbler:
        praise_list.append("플라스틱 컵 대신 **텀블러**를 살포시 꺼낼 때 정말 감동이었어.")
    if recycling:
        praise_list.append("꼼꼼하게 **분리수거**해 준 덕분에 쓰레기가 보물로 변했지 뭐야.")
    if "계단 이용" in green_actions:
        praise_list.append("엘리베이터 대신 **계단**을 오르는 너의 씩씩한 모습이 멋졌어.")

    if transport in ["자동차", "오토바이"]:
        regret_list.append(f"**{transport}**에서 나온 연기 때문에 조금 답답하긴 했어.")
    if meal == "육류 위주 식사":
        regret_list.append("오늘 식사에 **고기**가 많아서 배출 가스가 조금 늘어났단다.")
    if disposables >= 3:
        regret_list.append(f"오늘 **일회용품을 {disposables}개**나 사용해서 살짝 마음이 아팠어.")

    intro = "안녕! 나는 너와 매일 함께 숨 쉬는 **지구**야. 🌍\n\n"
    middle = "오늘 너의 하루는 나에게 선물 같은 하루였어! " if score >= 80 else "오늘 하루도 나와 함께 노력해 줘서 고마워. "
    
    praise_text = " " + " ".join(praise_list) if praise_list else " 소소한 친환경 실천들을 시작해 보려는 네 모습이 고마워."
    regret_text = "\n\n하지만 " + " ".join(regret_list) if regret_list else ""
    outro = "\n\n내일은 작은 것 하나라도 나와 약속해 줄래? 늘 곁에서 널 응원할게! 💚"
    
    return intro + middle + praise_text + regret_text + outro

def check_badges(transport, recycling, tumbler, green_actions, score):
    """달성한 배지 목록을 반환합니다."""
    badges = []
    if score >= 85: badges.append("🏅 탄소 히어로")
    if recycling: badges.append("🏅 분리수거 마스터")
    if tumbler: badges.append("🏅 텀블러 챔피언")
    if transport in ["도보", "자전거", "버스", "지하철"]: badges.append("🏅 그린 라이더")
    if len(green_actions) >= 3: badges.append("🏅 실천왕 프로")
    return badges

QUOTES = [
    "\"지구는 모든 사람의 필요를 충족시키기에 충분하지만, 탐욕을 충족시키기엔 부족하다.\" - 마하트마 간디",
    "\"우리가 지구를 다루는 방식이 곧 우리 아이들을 다루는 방식이다.\" - 윈델 베리",
    "\"자연은 서두르지 않지만, 모든 것을 이룬다.\" - 노자"
]

# ==========================================
# 3. Streamlit 화면 UI 구성
# ==========================================

st.sidebar.header("📋 오늘의 행동 기록")
st.sidebar.caption("오늘 당신의 생활습관을 솔직하게 기록해 주세요!")

transport = st.sidebar.selectbox("🚗 주요 이동수단", ["도보", "자전거", "버스", "지하철", "자동차", "오토바이"])
meal = st.sidebar.radio("🍽 오늘 식사 유형", ["채식", "일반식", "육류 위주 식사"])
elec_time = st.sidebar.slider("⚡ 전기/가전 사용 시간 (시간)", 0, 24, 8)
shower_time = st.sidebar.select_slider("🚿 샤워 시간", options=[5, 10, 20, 30], value=10, format_func=lambda x: f"{x}분")
disposables = st.sidebar.number_input("🛍 일회용품 사용 개수", min_value=0, max_value=10, value=2)

st.sidebar.markdown("---")
st.sidebar.subheader("✨ 친환경 실천 체크")
recycling = st.sidebar.checkbox("♻ 올바른 분리수거 실천", value=True)
tumbler = st.sidebar.checkbox("🥤 텀블러/다회용 컵 사용", value=False)

green_actions = st.sidebar.multiselect(
    "🌱 오늘 실천한 행동 (복수 선택)",
    ["대중교통 이용", "계단 이용", "에어컨/난방 절약", "음식 남기지 않기", "장바구니 사용"]
)

# 데이터 계산
total_emission, breakdown = calculate_emissions(
    transport, meal, elec_time, shower_time, disposables, recycling, tumbler, green_actions
)
score = calculate_eco_score(total_emission, recycling, tumbler, green_actions)
status_label, emoji = get_earth_status(score)
trees = round(max(0.0, AVERAGE_DAILY_EMISSION - total_emission) / 0.018, 1)

# 메인 타이틀
st.title("🌱 Eco Diary : 탄소발자국 탐정")
st.subheader("\"오늘의 행동이 지구에게 어떤 하루를 만들어 주었을까요?\"")

st.info(random.choice(QUOTES))
st.markdown("---")

# 대시보드 메트릭 카드
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <h4>오늘의 탄소배출량</h4>
        <h2 style="color:#2E7D32;">{total_emission} <small>kg CO₂</small></h2>
    </div>
    """, unsafe_allow_dict=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <h4>친환경 점수</h4>
        <h2 style="color:#1565C0;">{score} <small>/ 100점</small></h2>
    </div>
    """, unsafe_allow_dict=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <h4>지구 건강도</h4>
        <h2>{emoji} <span style="font-size:1.2rem;">{status_label}</span></h2>
    </div>
    """, unsafe_allow_dict=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <h4>나무 효과</h4>
        <h2 style="color:#2E7D32;">🌲 {trees} <small>그루</small></h2>
    </div>
    """, unsafe_allow_dict=True)

st.markdown("<br>", unsafe_allow_dict=True)

# 차트 시각화
left_col, right_col = st.columns(2)

with left_col:
    st.subheader("📊 친환경 점수 게이지")
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "#2ECC71"},
            'steps': [
                {'range': [0, 35], 'color': "#FFCDD2"},
                {'range': [35, 70], 'color': "#FFF9C4"},
                {'range': [70, 100], 'color': "#C8E6C9"}
            ]
        }
    ))
    fig_gauge.update_layout(height=280, margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig_gauge, use_container_width=True)

with right_col:
    st.subheader("🔍 항목별 탄소 배출 분석")
    df_breakdown = pd.DataFrame(list(breakdown.items()), columns=["항목", "배출량(kg)"])
    fig_bar = px.bar(
        df_breakdown, 
        x="항목", 
        y="배출량(kg)", 
        color="항목",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig_bar.update_layout(height=280, showlegend=False, margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")

# 지구의 편지 및 배지
st.subheader("💌 오늘 지구가 보낸 일기 편지")

letter_text = generate_earth_letter(transport, meal, disposables, recycling, tumbler, green_actions, score)
st.markdown(f"""
<div class="earth-letter">
    {letter_text.replace('\n', '<br>')}
</div>
""", unsafe_allow_dict=True)

st.markdown("<br>", unsafe_allow_dict=True)

st.subheader("🏅 오늘 획득한 배지")
badges = check_badges(transport, recycling, tumbler, green_actions, score)

if badges:
    badge_html = "".join([f'<span class="badge-box">{b}</span>' for b in badges])
    st.markdown(badge_html, unsafe_allow_dict=True)
else:
    st.caption("아직 획득한 배지가 없어요. 친환경 실천 항목을 늘려보세요!")

st.markdown("---")

# 미션 & 퀴즈
col_mission, col_quiz = st.columns(2)

with col_mission:
    st.subheader("🎯 오늘의 친환경 미션")
    st.success("✅ **[내일의 추천 미션]** 텀블러 소지하고 플라스틱 컵 사용 1회 줄이기!")
    st.progress(score / 100)

with col_quiz:
    st.subheader("💡 환경 상식 퀴즈")
    quiz_ans = st.radio("Q. 종이컵 1개를 사용할 때 발생하는 탄소량은 약 몇 g일까요?", ["1g", "11g", "100g"], index=0)
    if st.button("정답 확인"):
        if quiz_ans == "11g":
            st.balloons()
            st.success("정답입니다! 종이컵 1개당 약 11g의 CO₂가 생성됩니다.")
        else:
            st.error("아쉽네요! 정답은 '11g'입니다.")
            
