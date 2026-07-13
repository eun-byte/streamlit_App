import streamlit as st
import random

st.set_page_config(
    page_title="🍽️ 오늘 뭐 먹지?",
    page_icon="🍜",
    layout="centered"
)

# CSS
st.markdown("""
<style>
.stApp{
    background-color:#FFF8F2;
}

.title{
    text-align:center;
    color:#ff69b4;
    font-size:40px;
    font-weight:bold;
}

.subtitle{
    text-align:center;
    color:#666;
    font-size:18px;
}

.card{
    background:white;
    padding:20px;
    border-radius:20px;
    box-shadow:0px 4px 10px rgba(0,0,0,0.15);
}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='title'>🍽️ 오늘 뭐 먹지?</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>날씨에 맞는 메뉴를 추천해드려요 💕</div>", unsafe_allow_html=True)

st.write("")

weather = st.selectbox(
    "🌤️ 오늘 날씨를 선택하세요",
    ["☀️ 맑음", "🌧️ 비", "❄️ 눈", "☁️ 흐림"]
)

foods = {
    "☀️ 맑음":[
        {
            "name":"🍜 냉면",
            "image":"https://images.unsplash.com/photo-1547592180-85f173990554",
            "cal":"450 kcal",
            "nutri":"탄수화물 70g | 단백질 18g | 지방 6g"
        },
        {
            "name":"🥗 샐러드",
            "image":"https://images.unsplash.com/photo-1546069901-ba9599a7e63c",
            "cal":"280 kcal",
            "nutri":"탄수화물 20g | 단백질 15g | 지방 12g"
        }
    ],

    "🌧️ 비":[
        {
            "name":"🥞 김치전",
            "image":"https://images.unsplash.com/photo-1504674900247-0877df9cc836",
            "cal":"420 kcal",
            "nutri":"탄수화물 38g | 단백질 12g | 지방 24g"
        },
        {
            "name":"🍲 칼국수",
            "image":"https://images.unsplash.com/photo-1515003197210-e0cd71810b5f",
            "cal":"510 kcal",
            "nutri":"탄수화물 65g | 단백질 20g | 지방 10g"
        }
    ],

    "❄️ 눈":[
        {
            "name":"🍲 김치찌개",
            "image":"https://images.unsplash.com/photo-1544025162-d76694265947",
            "cal":"550 kcal",
            "nutri":"탄수화물 35g | 단백질 28g | 지방 22g"
        },
        {
            "name":"🍜 국밥",
            "image":"https://images.unsplash.com/photo-1555939594-58d7cb561ad1",
            "cal":"630 kcal",
            "nutri":"탄수화물 60g | 단백질 35g | 지방 18g"
        }
    ],

    "☁️ 흐림":[
        {
            "name":"🍝 파스타",
            "image":"https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9",
            "cal":"620 kcal",
            "nutri":"탄수화물 75g | 단백질 22g | 지방 18g"
        },
        {
            "name":"🍚 비빔밥",
            "image":"https://images.unsplash.com/photo-1604908176997-125f25cc6f3d",
            "cal":"560 kcal",
            "nutri":"탄수화물 65g | 단백질 20g | 지방 15g"
        }
    ]
}

if st.button("💕 메뉴 추천받기"):

    menu = random.choice(foods[weather])

    st.balloons()

    st.markdown("<div class='card'>", unsafe_allow_html=True)

    st.header(menu["name"])

    st.image(menu["image"], use_container_width=True)

    st.success(f"🔥 칼로리 : {menu['cal']}")

    st.info(f"🥗 영양소\n\n{menu['nutri']}")

    st.write("💖 **추천 이유**")

    if weather=="☀️ 맑음":
        st.write("더운 날엔 시원한 음식이 최고예요! 😋")

    elif weather=="🌧️ 비":
        st.write("비 오는 날엔 따뜻한 음식과 전이 잘 어울려요 ☔")

    elif weather=="❄️ 눈":
        st.write("추운 날엔 뜨끈한 국물이 최고랍니다 ❄️")

    else:
        st.write("오늘은 든든하게 한 끼 어떠세요? 😊")

    st.markdown("</div>", unsafe_allow_html=True)

st.write("")
st.caption("Made with ❤️ Streamlit")
