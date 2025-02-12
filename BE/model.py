import os
import re
from datetime import datetime, timedelta
from dotenv import load_dotenv
import google.generativeai as genai
from google.api_core import retry
from pymongo import MongoClient

# 환경 변수 로드
load_dotenv()
gemini_api = os.environ.get("Gemini_API_KEY")
genai.configure(api_key= gemini_api)

# MongoDB 연결 설정
connection_string = os.environ.get("DB_connection_string")
client = MongoClient(connection_string)
db = client['Conference']
article_collection = db["article"]

# Gemini 모델 설정
model = genai.GenerativeModel("gemini-pro")

# 사용자의 뉴스 히스토리 저장 (세션 유지)
user_news = ""  # 전역 변수

# MongoDB에서 뉴스 데이터 로드 (JSON 파일 대신)
def load_data():
    articles = list(article_collection.find({}))
    # ObjectId 등 JSON 직렬화에 문제가 되는 항목은 문자열로 변환합니다.
    for article in articles:
        if "_id" in article:
            article["_id"] = str(article["_id"])
    return articles

# 질문에서 날짜와 분야(섹션) 추출
def extract_date_section(question):
    keywords = {
        "경제": "경제", 
        "정치": "정치", 
        "사회": "사회", 
        "생활문화": "생활문화", 
        "IT과학": "IT과학",
        "세계": "세계",
        "경재": "경제",
        "세게": "세계",
        "생활": "생활문화화",
        "IT": "IT과학",   
        "it": "IT과학",   
        "아이티": "IT과학" 
    }
    section, date = None, None

    # 기본 날짜: 오늘
    date = datetime.today().strftime("%Y-%m-%d")

    # 질문에 "어제"가 포함된 경우 어제 날짜로 설정
    if "어제" in question:
        date = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    else:
        # "2월 7일" 또는 "2/7" 형식의 날짜 추출
        match = re.search(r"(\d{1,2})월\s*(\d{1,2})일", question) or re.search(r"(\d{1,2})/(\d{1,2})", question)
        if match:
            month, day = match.groups()
            date = datetime(datetime.today().year, int(month), int(day)).strftime("%Y-%m-%d")

    # 뉴스 분야(섹션) 추출
    question_lower = question.lower()
    for key, cat in keywords.items():
        if key.lower() in question_lower:
            section = cat
            break

    return date, section

# Gemini 모델을 사용하여 질문 유형을 분류
def classify_question(question):
    prompt = f"""
    사용자의 질문을 보고 아래 중 하나로 분류하세요.
    1. 뉴스 요청 (예: "어제의 경제 뉴스 분석해줘", "2월 7일 정치 뉴스 요약해줘", "세계 뉴스 알려줘", "IT 뉴스")
    2. 일반 개념 질문 (예: "환율이 뭐야?", "금리가 뭐야?", "GDP란?")
    3. 일상 대화 (예: 안녕, 하이, 오랜만이야, 배고파, 날씨 좋다, 오늘 날씨 어때?, 친구 짜증난다)
    
    사용자의 질문: "{question}"

    질문 유형:
    """
    try:
        response = model.generate_content(prompt, request_options={'retry': retry.Retry()})
        return response.text.strip()
    except Exception as e:
        return f" Gemini error: {str(e)}"

# 판별된 유형에 따라 적절한 응답 제공
def summarize(question):
    global user_news

    question_type = classify_question(question)

    if "뉴스 요청" in question_type:
        date, section = extract_date_section(question)

        if not section:
            return "분야를 인식할 수 없습니다. '경제 뉴스 알려줘', '정치 뉴스 궁금해'처럼 입력해주세요."

        news_articles = load_data()
        filtered_news = [article for article in news_articles if article.get("date") == date and article.get("section") == section]

        if not filtered_news:
            return f"❌ {date}의 {section} 뉴스가 없습니다. ❌"

        # 필터링된 뉴스를 하나의 문자열로 결합하여 세션에 저장
        user_news = "\n\n".join([f"제목: {article.get('title', '제목없음')}\n내용: {article.get('content', '내용없음')}" for article in filtered_news])

        prompt = f"""
        다음은 {date}의 {section} 뉴스 기사입니다. 이를 바탕으로 뉴스 요약을 제공하세요.
        1. 여러 개의 뉴스들을 보고, 공통된 흐름이나 트렌드를 알려주세요.
        2. 중요한 뉴스라고 생각된다면, 따로 요약해서 알려주세요.
        3. 전문 용어 등의 어려운 개념은 설명을 추가해주세요.

        {user_news}

        뉴스 분석:
        """

    elif "일반 개념 질문" in question_type:
        prompt = f"""
        사용자의 질문: {question}

        너가 위에서 분석한 설명이나 뉴스에서 어떤 의미로 쓰였는지 같이 설명해주세요.

        뉴스나 설명에 없는 용어라면, 일반적인 지식을 바탕으로 답변하세요.

        관련 뉴스: {user_news}
        """
    else: 
        prompt = f"""
        {question}
        """

    try:
        response = model.generate_content(prompt, request_options={'retry': retry.Retry()})
        return response.text
    except Exception as e:
        return f" Gemini error: {str(e)}"


question = "최근 IT 뉴스 요약해줘"
answer = summarize(question)
print(answer)