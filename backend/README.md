## 🛡️ MLD Web - Backend

파일 분석 요청 처리, 모델 예측 수행, 결과 반환 및 보고서(PDF) 추출 기능, 비로그인 사용자 업로드 갯수 제한
, 로그인/마이페이지 등을 제공.  
FastAPI 기반의 비동기 REST API 서버로, 확장성과 유지보수성을 고려한 구조로 설계.

---

## 🌐 API 서버 배포 주소
👉 [API 서버 배포 주소](http://13.125.214.199:8000)

---

## 🔧 배포 
AWS Ec2 + AWS RDS(Docker) 

---

## ✅ 향후 계획

- 파일 업로드 부분 시큐어 코딩
- 파일 전처리 속도 개선
---

## 🛠️ 사용 기술 스택

<div align="center">

<img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
<img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
<img src="https://img.shields.io/badge/Uvicorn-44A833?style=for-the-badge&logo=uvicorn&logoColor=white" />
<img src="https://img.shields.io/badge/SQLAlchemy-336791?style=for-the-badge&logo=sqlalchemy&logoColor=white" />
<img src="https://img.shields.io/badge/PostgreSQL-336791?style=for-the-badge&logo=postgresql&logoColor=white" />
<img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" />

</div>


---

## 📂 프로젝트 구조
```
backend/
├── app/
│   ├── api/
│   │   └── endpoints/
│   │       ├── files.py    -> 사용 X : /predict, /piechart, /meta API 정의 
|   |       ├── ai_integrate_reports.py  -> 사용 X : /files/report API 정의
|   |       ├── analyze_ful.py -> 파일 분석 부터 ~ PDF 보고서 출력 까지 모든 결과 출력 API
|   |       ├── history_download.py -> 마이페이지에서 PDF 요청시 데베 값으로 부터 보고서 재 생성 
|   |       ├── history.py ->  DB에 저장된 결과 마이페이지에 반환하는 API
|   |       ├── upload_limit.py ->  비로그인 사용자 업로드 갯수 제한
|   |       ├── users.py -> 사용자 로그인
│   │       └── report_legacy.py
│   ├── assets/
│   │   ├── CNN_exe.pth
│   │   ├── Randomforest_pdf.pkl
│   │   ├── ae_hwp.pth
│   │   ├── ae_docx.pth
│   │   ├── ae_xlsx.pth
│   │   ├── fonts/
│   │   │   ├── NotoSansKR-Bold.ttf
│   │   │   └── NotoSansKR-Regular.ttf
│   │   └── images/
│   │       └── report_logo.png
│   ├── core/ -> 사용 X
│   │   ├── config.py
│   │   └── security.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py -> DB 연결 및 세션, SessionLocal, engine, get_db()
│   │   └── session.py -> 사용 X
│   ├── db_model/
│   │   └── users.py -> user db 정의
│   ├── db_persistence/
│   │   ├── analysis.py -> DB에 분석 결과 저장
│   │   └── user.py -> 회원 가입 시 DB에 회원 id,pw 저장
│   ├── models/
│   │   ├── auto_encoder_model.py
│   │   ├── cnn_model.py
│   │   ├── rf_model.py
│   │   ├── file.py
│   │   └── users.py
│   ├── schemas/
│   │   ├── analysis.py -> Pydantic 스키마, API 응답용 모델
│   │   └── users.py -> 스키마 초기화용
│   ├── services/
│   │   ├── auth_service/
│   │   │   ├── auth.py
│   │   │   └── oauth.py
│   │   ├── ai_autoencoder_reports.py
│   │   ├── ai_cnn_reports.py
│   │   ├── ai_db_reports.py
│   │   ├── ai_integrate_reports.py
│   │   ├── ai_rf_reports.py
│   │   ├── cleanup.py
│   │   ├── prediction.py
│   │   └── redis_client.py
│   ├── utils/
│   │   ├── file_processing.py
│   │   ├── image_converter.py
│   │   ├── model_info.py
│   │   ├── pdfid_info.py
│   │   └── performance_timer.py
│   ├── __init__.py
│   ├── init_db.py
│   └── main.py
├── temp_uploads/
│   └── input/
│   └── output/
├── .dockerignore
├── .env
├── .gitattribute
├── .gitignore
├── .docker-compose.yml
├── Dockerfile
├── README.md
└── requirements.txt

```

