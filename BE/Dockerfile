# Python 3.9 이미지를 기반으로 설정
FROM python:3.9-slim

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 파일들을 컨테이너로 복사
COPY requirements.txt .
COPY app.py .
COPY .env .

# 필요한 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# 포트 설정
EXPOSE 5000

# 애플리케이션 실행
CMD ["python", "app.py"] 