### app/db_persistence/user.py
from sqlalchemy.orm import Session
from app.db_model.users import User
from app.services.auth_service.auth import hash_password

from app.schemas.users import UserCreate

def create_user(db: Session, user: UserCreate):
    db_user = User(
        username=user.username,
        hashed_password=hash_password(user.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_user_by_id(db: Session, user_id):
    return db.query(User).filter(User.id == user_id).first()