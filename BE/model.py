import json
import os
import re
from datetime import datetime, timedelta
from dotenv import load_dotenv
import google.generativeai as genai
from google.api_core import retry

# 환경 변수 로드
load_dotenv()
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

# Gemini 모델 설정
gemini_model = genai.GenerativeModel("gemini-pro")

# 뉴스 데이터 JSON 파일 경로
NEWS_JSON_FILE = "news_data.json"

# 사용자별 세션 유지
user_history = {}

# json 데이터 로드드
def load_data():
    with open(NEWS_JSON_FILE, "r", encoding="utf-8") as file:
        return json.load(file)

# 질문에서 날짜와 분야야 추출
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

    # date 기본값을 오늘로 설정
    date = datetime.today().strftime("%Y-%m-%d")

    # date 파싱 (질문에서 날짜가 주어진 경우)
    if "어제" in question:
        date = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    else:
        match = re.search(r"(\d{1,2})월\s*(\d{1,2})일", question) or re.search(r"(\d{1,2})/(\d{1,2})", question)
        if match:
            month, day = match.groups()
            date = datetime(datetime.today().year, int(month), int(day)).strftime("%Y-%m-%d")

    # 뉴스 분야 추출
    question_lower = question.lower()
    for key, cat in keywords.items():
        if key.lower() in question_lower:
            section = cat
            break

    return date, section

# 질문 판별
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
        response = gemini_model.generate_content(prompt, request_options={'retry':retry.Retry()})
        return response.text.strip()
    except Exception as e:
        return f" Gemini error: {str(e)}"

# 판별된 유형에 따라 적절한 응답 제공공
def summarize(user_id, question):
    question_type = classify_question(question)

    if "뉴스 요청" in question_type:
        date, section = extract_date_section(question)

        if not section:
            return "분야를 인식할 수 없습니다. '경제 뉴스 알려줘', '정치 뉴스 궁금해'처럼 입력해주세요."

        news_articles = load_data()
        filtered_news = [article for article in news_articles if article["date"] == date and article["section"] == section]

        if not filtered_news:
            return f"❌ {date}의 {section} 뉴스가 없습니다. ❌"

        # 검색된 뉴스를를 캐시에 저장 (세션 유지)
        user_history[user_id] = "\n\n".join([f"제목: {article['title']}\n내용: {article['content']}" for article in filtered_news])

        prompt = f"""
        다음은 {date}의 {section} 뉴스 기사입니다. 이를 바탕으로 뉴스 요약을 제공하세요.
        1. 여러 개의 뉴스들을 보고, 공통된 흐름이나 트렌드를 알려주세요.
        2. 중요한 뉴스라고 생각된다면, 따로 요약해서 알려주세요.
        3. 전문 용어 등의 어려운 개념은 설명을 추가해주세요.

        {user_history[user_id]}

        뉴스 분석:
        """

    elif "일반 개념 질문" in question_type:
        related_news = user_history.get(user_id, "")
        prompt = f"""
        사용자의 질문: {question}

        만약 관련 뉴스가 있다면 참고하세요:
        {related_news}

        관련 뉴스 내용이 없으면, 일반적인 지식을 바탕으로 답변하세요.
        """

    else: 
        prompt = f"""
        {question}
        """

    try:
        response = gemini_model.generate_content(prompt, request_options={'retry':retry.Retry()})
        return response.text
    except Exception as e:
        return f" Gemini error: {str(e)}"


if __name__ == "__main__":
    user_id = "user_123"  # 세션을 유지할 사용자 ID

    print("\n🔵 뉴스 분석 및 경제 질문 AI 🔵")
    print("질문을 입력하세요. (종료하려면 'exit' 입력)")

    while True:
        user_question = input("\n📢 질문: ")

        if user_question.lower() == "exit":
            print("🔴 프로그램 종료.")
            break

        response = summarize(user_id, user_question)
        print(f"\n📝 응답: {response}")