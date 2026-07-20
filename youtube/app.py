import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
from konlpy.tag import Okt
from googleapiclient.discovery import build
from urllib.parse import urlparse, parse_qs
import re

# ======================
# 페이지 설정
# ======================
st.set_page_config(
    page_title='유튜브 댓글 분석기',
    page_icon='📊',
    layout='wide'
)

# ======================
# API 설정
# ======================
API_KEY = st.secrets['YOUTUBE_API_KEY']
youtube = build('youtube', 'v3', developerKey=API_KEY)

# ======================
# 유틸 함수
# ======================
def extract_video_id(url):
    patterns = [
        r'(?:v=|/)([0-9A-Za-z_-]{11}).*',
        r'youtu\\.be/([0-9A-Za-z_-]{11})'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

@st.cache_data(ttl=3600)
def get_video_info(video_id):
    request = youtube.videos().list(
        part='snippet,statistics',
        id=video_id
    )
    response = request.execute()

    if not response['items']:
        return None

    item = response['items'][0]

    return {
        'title': item['snippet']['title'],
        'channel': item['snippet']['channelTitle'],
        'views': int(item['statistics'].get('viewCount', 0)),
        'likes': int(item['statistics'].get('likeCount', 0)),
        'comments': int(item['statistics'].get('commentCount', 0))
    }

@st.cache_data(ttl=3600)
def get_comments(video_id, max_comments=500):
    comments = []
    next_page_token = None

    progress_bar = st.progress(0)
    status_text = st.empty()

    while len(comments) < max_comments:
        request = youtube.commentThreads().list(
            part='snippet',
            videoId=video_id,
            maxResults=100,
            pageToken=next_page_token,
            order='time'
        )

        response = request.execute()

        for item in response['items']:
            comment = item['snippet']['topLevelComment']['snippet']

            comments.append({
                'text': comment['textDisplay'],
                'published': comment['publishedAt'],
                'likeCount': comment['likeCount'],
                'author': comment['authorDisplayName']
            })

            if len(comments) >= max_comments:
                break

        progress = min(len(comments) / max_comments, 1.0)
        progress_bar.progress(progress)
        status_text.text(f'댓글 수집 중... {len(comments)}/{max_comments}')

        next_page_token = response.get('nextPageToken')

        if not next_page_token:
            break

    progress_bar.empty()
    status_text.empty()

    return pd.DataFrame(comments)

# 간단 감성분석
POSITIVE_WORDS = ['좋', '최고', '재밌', '웃기', '감사', '사랑', '대박', '멋지', '훌륭']
NEGATIVE_WORDS = ['싫', '별로', '최악', '지루', '화나', '실망', '짜증', '아쉽']

def analyze_sentiment(text):
    text = str(text)

    pos_score = sum(1 for word in POSITIVE_WORDS if word in text)
    neg_score = sum(1 for word in NEGATIVE_WORDS if word in text)

    if pos_score > neg_score:
        return '긍정'
    elif neg_score > pos_score:
        return '부정'
    else:
        return '중립'

# ======================
# UI
# ======================
st.title('📊 유튜브 댓글 분석기')
st.markdown('**영상 링크를 입력하면 댓글을 수집하고 시간대별 추이, 감성분석, 워드클라우드를 생성합니다.**')

# 입력 영역
col1, col2 = st.columns([4, 1])

with col1:
    video_url = st.text_input(
        '유튜브 영상 URL',
        placeholder='https://www.youtube.com/watch?v=...'
    )

with col2:
    comment_count = st.selectbox(
        '댓글 수',
        [100, 300, 500, 1000],
        index=2
    )

# 분석 버튼
if st.button('🚀 분석 시작', type='primary'):

    if not video_url:
        st.error('유튜브 URL을 입력하세요.')
        st.stop()

    video_id = extract_video_id(video_url)

    if not video_id:
        st.error('올바른 유튜브 URL이 아닙니다.')
        st.stop()

    # ======================
    # 영상 정보
    # ======================
    with st.spinner('영상 정보 가져오는 중...'):
        info = get_video_info(video_id)

    if not info:
        st.error('영상을 찾을 수 없습니다.')
        st.stop()

    st.subheader('🎬 영상 정보')

    col1, col2 = st.columns([1, 1])

    with col1:
        st.video(video_url)

    with col2:
        st.markdown(f'### {info["title"]}')
        st.write(f'**채널:** {info["channel"]}')
        st.write(f'**조회수:** {info["views"]:,}')
        st.write(f'**좋아요:** {info["likes"]:,}')
        st.write(f'**전체 댓글:** {info["comments"]:,}')

    st.divider()

    # ======================
    # 댓글 수집
    # ======================
    st.subheader('💬 댓글 수집')

    df = get_comments(video_id, comment_count)

    if df.empty:
        st.warning('댓글을 수집할 수 없습니다.')
        st.stop()

    st.success(f'총 {len(df):,}개의 댓글을 수집했습니다.')

    # 날짜 처리
    df['published'] = pd.to_datetime(df['published'])
    df['date'] = df['published'].dt.date
    df['hour'] = df['published'].dt.hour

    # 감성분석
    df['sentiment'] = df['text'].apply(analyze_sentiment)

    # ======================
    # KPI
    # ======================
    st.subheader('📈 핵심 지표')

    positive_rate = (df['sentiment'] == '긍정').mean() * 100
    negative_rate = (df['sentiment'] == '부정').mean() * 100
    avg_likes = df['likeCount'].mean()

    k1, k2, k3, k4 = st.columns(4)

    k1.metric('수집 댓글', f'{len(df):,}')
    k2.metric('긍정 비율', f'{positive_rate:.1f}%')
    k3.metric('부정 비율', f'{negative_rate:.1f}%')
    k4.metric('평균 좋아요', f'{avg_likes:.1f}')

    # ======================
    # 시간대별 추이
    # ======================
    st.subheader('🕒 시간대별 댓글 작성 추이')

    hourly = df.groupby('hour').size().reset_index(name='count')

    fig_hour = px.line(
        hourly,
        x='hour',
        y='count',
        markers=True,
        title='시간대별 댓글 수'
    )

    fig_hour.update_layout(
        xaxis_title='시간',
        yaxis_title='댓글 수',
        height=400
    )

    st.plotly_chart(fig_hour, use_container_width=True)

    # ======================
    # 날짜별 추이
    # ======================
    st.subheader('📅 날짜별 댓글 추이')

    daily = df.groupby('date').size().reset_index(name='count')

    fig_daily = px.bar(
        daily,
        x='date',
        y='count',
        title='날짜별 댓글 수'
    )

    st.plotly_chart(fig_daily, use_container_width=True)

    # ======================
    # 감성 분포
    # ======================
    st.subheader('😊 댓글 반응도')

    sentiment_counts = df['sentiment'].value_counts().reset_index()
    sentiment_counts.columns = ['sentiment', 'count']

    fig_sentiment = px.pie(
        sentiment_counts,
        names='sentiment',
        values='count',
        title='감성 분포',
        color='sentiment',
        color_discrete_map={
            '긍정': '#2ecc71',
            '중립': '#95a5a6',
            '부정': '#e74c3c'
        }
    )

    st.plotly_chart(fig_sentiment, use_container_width=True)

    # ======================
    # 워드클라우드
    # ======================
    st.subheader('☁️ 한글 워드클라우드')

    okt = Okt()

    # 명사 추출
    nouns = []

    for text in df['text']:
        try:
            nouns.extend(okt.nouns(str(text)))
        except:
            continue

    # 불용어 제거
    stopwords = {
        '영상', '진짜', '너무', '정말', '그냥', '이거', '저거',
        '댓글', '사람', '생각', '때문', '하나', '지금', '오늘'
    }

    filtered_nouns = [
        noun for noun in nouns
        if len(noun) >= 2 and noun not in stopwords
    ]

    if filtered_nouns:
        word_freq = Counter(filtered_nouns)

        wc = WordCloud(
            font_path='fonts/NanumGothic.ttf',
            width=1200,
            height=500,
            background_color='white',
            max_words=100
        ).generate_from_frequencies(word_freq)

        fig, ax = plt.subplots(figsize=(15, 6))
        ax.imshow(wc, interpolation='bilinear')
        ax.axis('off')

        st.pyplot(fig)

        # 상위 키워드
        st.markdown('#### 🔥 상위 키워드')

        top_words = pd.DataFrame(
            word_freq.most_common(15),
            columns=['키워드', '빈도']
        )

        st.dataframe(top_words, use_container_width=True)

    # ======================
    # 인기 댓글
    # ======================
    st.subheader('👍 좋아요 많은 댓글')

    top_comments = df.nlargest(5, 'likeCount')[
        ['author', 'likeCount', 'text']
    ]

    for idx, row in top_comments.iterrows():
        with st.container():
            st.markdown(f'**{row["author"]}** · 👍 {row["likeCount"]}')
            st.markdown(row['text'], unsafe_allow_html=True)
            st.divider()

    # ======================
    # 원본 데이터
    # ======================
    st.subheader('📋 원본 댓글 데이터')

    display_df = df[['published', 'author', 'likeCount', 'sentiment', 'text']]
    st.dataframe(display_df, use_container_width=True)

    # 다운로드
    csv = display_df.to_csv(index=False).encode('utf-8-sig')

    st.download_button(
        label='📥 CSV 다운로드',
        data=csv,
        file_name=f'youtube_comments_{video_id}.csv',
        mime='text/csv'
    )

# ======================
# 사이드바
# ======================
with st.sidebar:
    st.header('ℹ️ 사용 방법')

    st.markdown('''
    1. 유튜브 영상 링크 입력
    2. 수집할 댓글 수 선택
    3. **분석 시작** 클릭

    ### 제공 기능
    - 🎬 영상 미리보기
    - 💬 댓글 수집
    - 🕒 시간대 분석
    - 📅 날짜별 추이
    - 😊 감성분석
    - ☁️ 한글 워드클라우드
    - 📥 CSV 다운로드
    ''')

    st.divider()

    st.caption('Streamlit Cloud 배포용 프로젝트')
YOUTUBE_API_KEY = "AIzaSyDjVDpNMP-FsJV6uWUcms8kJ3adAiypAyo"
