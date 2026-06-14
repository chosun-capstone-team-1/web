## app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from app.api.endpoints import files
from app.api.endpoints import analyze_full
from app.api.endpoints import ai_integrate_reports
from app.api.endpoints import users, history, history_download
from fastapi_utils.tasks import repeat_every  
from app.services.cleanup import clean_old_reports
from app.api.endpoints import upload_limit
from app.init_db import init_db

import os

app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
default_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://web-front-test.netlify.app",
]
extra_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "").split(",")
    if origin.strip()
]
origins = default_origins + extra_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


##  FastAPI 앱 시작 시 주기적으로 업로드 파일 및 pdf 생성 삭제
@app.on_event("startup")
def startup_database_init():
    init_db()


@app.on_event("startup")
@repeat_every(seconds=1800)  # 10분마다 실행, 30분 : 1800, 1시간 : 3600
def scheduled_cleanup_task():
    print("[백그라운드 작업] 오래된 PDF 정리 시작")
    clean_old_reports()

# 비로그인시 업로드 제한 API
app.include_router(upload_limit.router, prefix="/limit", tags=["limit"])

# 사용자 파일 업로드 임시 저장
os.makedirs("./temp_uploads/input", exist_ok=True)
os.makedirs("./temp_uploads/output", exist_ok=True)

# 사용자 회원가입/로그인
app.include_router(users.router, prefix="/users", tags=["users"])

# 마이페이지 API
app.include_router(history.router, prefix="/history", tags=["history"])
app.include_router(history_download.router, prefix="/history", tags=["history"])

# 분석 API
app.include_router(analyze_full.router, prefix="", tags=["Full Analyze"])
# PDF 파일 다운로드 시 경로
app.mount("/static", StaticFiles(directory="temp_uploads/output"), name="static")

app.include_router(ai_integrate_reports.router, prefix="/files")


# 루트 접속 시 안내 페이지
# @app.get("/", response_class=HTMLResponse)
# def read_root():
#     return """
#     <html>
#         <head>
#             <meta name="robots" content="noindex, nofollow">
#             <title>테스트용 API 서버</title>
#         </head>
#         <body style="font-family: sans-serif;">
#             <h2>🔒 내부 테스트용 백엔드 API 서버입니다.</h2>
#             <p>이 서버는 <b>웹 개발 확인용</b>이며, 외부에 공개된 서비스가 아닙니다.</p>
#             <p>검색 엔진에 노출되지 않도록 <code>robots</code> 설정이 적용되어 있습니다.</p>
#         </body>
#     </html>
#     """

# 검색 로봇 접근 차단
@app.get("/robots.txt", response_class=PlainTextResponse)
def robots_txt():
    return "User-agent: *\nDisallow: /"

