### app/schemas/users.py
from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID
from datetime import datetime

class UserCreate(BaseModel):
    username: str           
    password: str

class UserLogin(BaseModel):
    username: str           
    password: str

class UserOut(BaseModel):
    id: UUID
    username: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True