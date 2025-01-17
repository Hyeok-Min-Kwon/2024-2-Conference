from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/ask', methods=['POST'])
def ask():
    data = request.json  # JSON 데이터 읽기
    question = data.get('question')  # "question" 추출

    # 답변 생성성
    answer = f"{question}"
    
    # JSON 응답 반환
    return jsonify({"answer": answer})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
