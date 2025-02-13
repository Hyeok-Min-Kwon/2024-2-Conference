from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import google.generativeai as genai
import os
from pymongo import MongoClient

# 환경 변수 로드
load_dotenv()
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

# Flask 앱 설정
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# MongoDB 연결 설정
connection_string = os.environ.get("MONGO_URI")
client = MongoClient(connection_string)
db = client['Conference']
article_collection = db["article"]

# Flask API 엔드포인트 (질문 분석 없이 바로 처리)
@app.route('/api/ask', methods=['POST'])
def ask():
    data = request.json
    question = data.get('question')

    try:
        # MongoDB에서 최근 뉴스 기사 10개를 가져옵니다.
        articles = list(
            article_collection.find(
                {}, 
                {"_id": 0, "title": 1, "content": 1, "date": 1}
            ).sort("date", -1).limit(20)
        )
        
        if not articles:
            return jsonify({"answer": "현재 뉴스 기사가 없습니다."})

        # 가져온 기사들을 텍스트로 조합
        articles_text = "\n\n".join([
            f"제목: {article.get('title', '제목 없음')}\n날짜: {article.get('date', '날짜 없음')}\n내용: {article.get('content', '내용 없음')}"
            for article in articles
        ])

        # Gemini 모델에 전달할 프롬프트 구성
        prompt = f"""
다음은 최근 뉴스 기사입니다:

{articles_text}

위 기사를 참고하여 아래 질문에 대해 답변해 주세요.
질문: {question}
답변:
        """

        # Gemini 모델을 이용해 답변 생성
        response = genai.GenerativeModel("gemini-pro").generate_content(prompt)
        answer = response.text

    except Exception as e:
        answer = f"An error occurred: {str(e)}"

    return jsonify({"answer": answer})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
