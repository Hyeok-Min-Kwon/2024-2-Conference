from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import openai
import os

# 환경 변수 로드
load_dotenv()
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Flask 앱 설정
app = Flask(__name__)
CORS(app)

@app.route('/api/ask', methods=['POST'])
def ask():
    data = request.json  # JSON 데이터 읽기
    question = data.get('question')  # 질문 추출

    try:
        response = openai.Client().chat.completions.create(
            model="gpt-3.5-turbo",  # 사용할 모델
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": question}
            ]
        )

        # 응답 데이터에서 답변 추출
        answer = response.choices[0].message.content.strip()

    except Exception as e:
        # 모든 예외 처리
        answer = f"An error occurred: {str(e)}"

    # JSON 응답 반환
    return jsonify({"answer": answer})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
