from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
import google.generativeai as genai
import os
import re
from datetime import datetime, timedelta
from pymongo import MongoClient

# 환경 변수 로드
load_dotenv()
gemini_api = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key= gemini_api)

# Flask 앱 설정
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "https://fom2024conference.vercel.app"}}, supports_credentials=True)

# MongoDB 연결 설정
connection_string = os.environ.get("DB_connection_string")
client = MongoClient(connection_string)
db = client['Conference']
article_collection = db["article"]

# LangChain에서 사용할 model
llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key="AIzaSyAaoCRxw6p2_ZcHZ_-O6g2TDTJ-djNJutQ", temperature=0.1)

# MongoDB에서 뉴스 검색
def search_news(query_dict):
    if not isinstance(query_dict, dict):
        try:
            query_dict = eval(query_dict)  # 문자열일 경우 `dict`로 변환
        except Exception as e:
            raise TypeError(f"검색 조건(query_dict)은 반드시 dict 타입이어야 합니다. 오류: {e}")

    results = list(article_collection.find(query_dict, {"_id": 0, "title": 1, "content": 1, "date": 1, "url": 1, "press": 1}).limit(30))
    return results if results else "해당 날짜의 뉴스가 없습니다."

# LangChain 검색기 연결
search_tool = Tool(
    name="MongoDB News Search",
    func=search_news,
    description="MongoDB에서 뉴스 검색 (date와 section을 입력하세요). section 내용은 한국어로 하세요."
)

# LangChain 에이전트 생성
agent = initialize_agent(
    tools=[search_tool],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    return_intermediate_steps=True
)

# 뉴스 기사 요약
def summarize_news(news_texts):
    prompt = f"""
        다음은 뉴스 기사 데이터입니다. 
        1. 주요 뉴스 내용을 요약하세요.
        2. 핵심 트렌드를 분석하세요.
        3. 중요한 내용을 정리해 주세요.
        4. 어려운 용어는 개념을 설명해주세요.

        {news_texts}
        """
    response = llm(prompt)
    return response

# Flask API 엔드포인트
@app.route('/api/ask', methods=['POST'])
def ask():
    data = request.json
    question = data.get('question')

    try:
        # LangChain 에이전트로 검색 수행
        response = agent.invoke(question)
        observations = response["intermediate_steps"]

        if observations:
            news_articles = observations[-1][1]
        else:
            return jsonify({"answer": "해당 날짜의 뉴스가 없습니다."})

        if isinstance(news_articles, list) and news_articles:
            news_texts = "\n\n".join([
                f"제목: {news['title']}\n날짜: {news['date']}\n내용: {news['content']}"
                for news in news_articles
            ])

        summary = summarize_news(news_texts)
        answer = summary

    except Exception as e:
        answer = f"An error occurred: {str(e)}"

    return jsonify({"answer": answer})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000, debug=False)
