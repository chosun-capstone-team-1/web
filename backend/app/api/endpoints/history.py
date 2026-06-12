# app/api/endpoints/history.py
# -> db_persistence/analysis.py 를 통해 저장된 db를 마이페이지에 반환하는 api 코드
from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.database.connection import get_db
from app.services.auth_service.auth import decode_access_token
from app.db_persistence.analysis import FileAnalysis, LogRecord, ModelInfo, PerformanceMetric
import uuid

router = APIRouter()


def _parse_user_id(value: str):
    try:
        return uuid.UUID(str(value))
    except (TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid or expired token")

@router.get("/my-analyses-full")
def get_my_full_analysis_history(authorization: str = Header(...), db: Session = Depends(get_db)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization Header")

    token = authorization.split(" ")[1]
    payload = decode_access_token(token)

    if payload is None or "user_id" not in payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_id = _parse_user_id(payload["user_id"])

    # 1. 유저의 모든 분석 결과 조회
    results = db.query(FileAnalysis).filter(FileAnalysis.user_id == user_id).all()

    # 2. 각 결과에 대해 연결된 로그, 모델 정보, 성능 정보 JOIN
    response = []
    for r in results:
        log = db.query(LogRecord).filter(LogRecord.analysis_id == r.analysis_id).first()
        model_info = db.query(ModelInfo).filter(ModelInfo.analysis_id == r.analysis_id).first()
        perf = db.query(PerformanceMetric).filter(PerformanceMetric.analysis_id == r.analysis_id).first()

        response.append({
            "analysis_id": str(r.analysis_id),
            "filename": r.filename,
            "file_size": r.file_size,
            "extension": r.extension,
            "sha256": r.sha256,
            "result": r.result,
            "confidence": r.confidence,
            "summary": r.summary,
            "report_url": r.report_url,
            "normal": r.normal,                
            "malicious": r.malicious,  
            "created_at": r.created_at.isoformat(),
            "log": {
                "start_time": log.start_time.isoformat() if log else None,
                "model_load": log.model_load if log else None,
                "preprocess": log.preprocess if log else None,
                "inference": log.inference if log else None
            },
            "model_info": {
                "type": model_info.type if model_info else None,
                "input": model_info.input if model_info else None,
                "train_size": model_info.train_size if model_info else None,
                "test_accuracy": model_info.test_accuracy if model_info else None
            },
            "performance": {
                "precision": perf.precision if perf else None,
                "recall": perf.recall if perf else None,
                "f1_score": perf.f1_score if perf else None,
                "benign_accuracy": perf.benign_accuracy if perf else None,
                "malware_accuracy": perf.malware_accuracy if perf else None
            }
        })

    return response
