# Python 이미지 기반
FROM python:3.10-slim

# 작업 디렉토리 설정
WORKDIR /app

# 종속성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY . .

# 포트 설정 (Render는 8000 사용)
EXPOSE 8000

# FastAPI 앱 실행 (main.py에 app 인스턴스 존재한다고 가정)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
