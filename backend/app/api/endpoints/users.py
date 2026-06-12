### app/api/endpoints/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.users import UserCreate, UserLogin, UserOut
from app.db_persistence import user as user_crud
from app.services.auth_service import auth
import logging

router = APIRouter()

@router.post("/register", response_model=UserOut)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = user_crud.get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return user_crud.create_user(db, user)


logger = logging.getLogger("uvicorn")  # FastAPI 기본 로거

@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    logger.info(f"[로그인 요청] username={user.username}")

    db_user = user_crud.get_user_by_username(db, user.username)
    if not db_user:
        logger.warning(f"[로그인 실패] 존재하지 않는 사용자: {user.username}")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not auth.verify_password(user.password, db_user.hashed_password):
        logger.warning(f"[로그인 실패] 비밀번호 불일치: {user.username}")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = auth.create_access_token({"user_id": str(db_user.id)})
    logger.info(f"[로그인 성공] user_id={db_user.id}, username={user.username}")
    return {"access_token": token, "token_type": "bearer"}
