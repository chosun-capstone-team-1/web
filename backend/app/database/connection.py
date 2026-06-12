# app/database/connection.py -> DB 연결 및 세션, SessionLocal, engine, get_db()
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# 이게 None이면 create_engine에서 오류 발생함
assert DATABASE_URL is not None, "DATABASE_URL 환경변수가 없습니다!"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
