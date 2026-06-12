# app/api/endpoints/upload_limit.py

from fastapi import APIRouter, Cookie, HTTPException, Request
from app.services.redis_client import redis_client

router = APIRouter()
MAX_UPLOAD_LIMIT = 3

@router.get("/upload-remaining")
def get_upload_remaining(request: Request, client_uuid: str = Cookie(default=None)):
    print(f"[쿠키 확인] client_uuid: {client_uuid}")  
    print("[전체 쿠키 확인]", request.cookies)

    if not client_uuid:
        raise HTTPException(status_code=400, detail="client_uuid 쿠키가 없습니다.")

    redis_key = f"uploads:{client_uuid}"
    current = redis_client.get(redis_key)

    used = int(current) if current else 0
    remaining = max(0, MAX_UPLOAD_LIMIT - used)

    return {
        "used": used,
        "remaining": remaining,
        "limit": MAX_UPLOAD_LIMIT
    }
