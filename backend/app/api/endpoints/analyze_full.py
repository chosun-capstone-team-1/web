# app/api/endpoints/analyze_full.py
import os, uuid, hashlib
from datetime import datetime
from fastapi import Cookie, Header,Depends, APIRouter, UploadFile, File, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.db_persistence.analysis import FileAnalysis, LogRecord, ModelInfo, PerformanceMetric
from app.services.prediction import load_model_by_extension, predict, predict_probabilities, ACCURACY_MAP
from app.services.ai_integrate_reports import generate_pdf_report_by_extension
from app.utils.model_info import extract_model_info, get_model_performance_score
from app.services.auth_service.auth import decode_access_token  # 사용자 인증 정보 파싱 함수 필요
from app.services.redis_client import redis_client

router = APIRouter()
## 비로그인 시 파일 업로드 횟수 제한
MAX_UPLOAD_LIMIT = 3
TTL_SECONDS = 3600 * 24  # 24시간 제한
SUPPORTED_EXTENSIONS = {"exe", "pdf"}


def _parse_log_datetime(value):
    if isinstance(value, datetime):
        return value
    if not value or value == "-":
        return None
    for fmt in ("%Y/%m/%d %H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(str(value), fmt)
        except ValueError:
            continue
    return None


def _ensure_supported_upload(ext: str, contents: bytes):
    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="EXE 또는 PDF 파일만 업로드할 수 있습니다.")

    if ext == "pdf":
        if b"%PDF-" not in contents[:1024]:
            raise HTTPException(
                status_code=400,
                detail="유효한 PDF 파일이 아닙니다. PDF 문서 형식이 아니면 분석할 수 없습니다."
            )
        return

    is_valid_pe = False
    if len(contents) >= 0x40 and contents[:2] == b"MZ":
        pe_offset = int.from_bytes(contents[0x3C:0x40], byteorder="little", signed=False)
        is_valid_pe = (
            pe_offset > 0
            and pe_offset + 4 <= len(contents)
            and contents[pe_offset:pe_offset + 4] == b"PE\x00\x00"
        )

    if not is_valid_pe:
        raise HTTPException(
            status_code=400,
            detail="유효한 Windows EXE 파일이 아닙니다. PE 실행 파일 형식이 아니면 분석할 수 없습니다."
        )


@router.post("/analyze-full")
async def analyze_full(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db), 
    authorization: str = Header(default=None),
    #token: str = Depends(oauth2_scheme)
    client_uuid: str = Cookie(default=None)
    
):
    
    # --- [1] 토큰 처리 및 로그인 여부 확인 ---
    user_id = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        payload = decode_access_token(token)
        if payload and "user_id" in payload:
            try:
                user_id = uuid.UUID(str(payload["user_id"]))
            except (TypeError, ValueError):
                user_id = None

    if not user_id:
        if not client_uuid:
            raise HTTPException(status_code=400, detail="비로그인 사용자는 UUID가 필요합니다.")

        redis_key = f"uploads:{client_uuid}"
        current_count = redis_client.get(redis_key)

        if current_count is None:
            redis_client.set(redis_key, 1, ex=TTL_SECONDS)  # TTL 24시간
        else:
            count = int(current_count)
            if count >= MAX_UPLOAD_LIMIT:
                raise HTTPException(status_code=429, detail="비로그인 사용자는 하루 3회까지만 업로드할 수 있습니다.")
            redis_client.incr(redis_key)


    # --- [2] 파일 저장 ---
    input_dir = "./temp_uploads/input"
    os.makedirs(input_dir, exist_ok=True)
    save_path = os.path.join(input_dir, file.filename)

    contents = await file.read()
    ext = os.path.splitext(file.filename)[1].lstrip(".").lower()
    _ensure_supported_upload(ext, contents)

    # 파일 저장
    with open(save_path, "wb") as f:
        f.write(contents)

    file_hash = hashlib.sha256(contents).hexdigest()
    file_size_mb = len(contents) / 1024 / 1024
    file_size_str = f"{file_size_mb:.2f} MB"

    try:
        load_model_by_extension(ext)
        result_data = predict(save_path, ext)
        prob_data = predict_probabilities(save_path, ext)
    except FileNotFoundError as e:
        if os.path.exists(save_path):
            os.remove(save_path)
        raise HTTPException(status_code=503, detail=str(e))
    except RuntimeError as e:
        if os.path.exists(save_path):
            os.remove(save_path)
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        if os.path.exists(save_path):
            os.remove(save_path)
        raise HTTPException(status_code=500, detail=f"분석 중 오류가 발생했습니다: {e}")

    model_info = extract_model_info(ext)
    model_performance = get_model_performance_score(ext)

    log_data = result_data.get("log", {})
    result_label = "악성" if prob_data["malicious"] >= 60 else "정상"

    confidence = result_data.get("accuracy")
    if confidence is None:
        confidence = ACCURACY_MAP.get(ext, None)
    summary = f"해당 \"{file.filename}\" 파일은 {result_label}으로 탐지되었으며, {prob_data['malicious']:.1f}%의 탐지 확률을 기반으로 판단됩니다."

    analysis_id = uuid.uuid4()

    # --- [3] PDF 생성 및 DB 저장은 로그인 유저만 ---
    static_url, display_name = None, None
    if user_id:
        pdf_path = generate_pdf_report_by_extension(
            file_path=save_path,
            ext=ext,
            result_data=result_data,
            prob_data=prob_data,
            user_id=user_id,
            analysis_id=analysis_id,
            original_filename=file.filename  # 사용자용 출력 파일명
        )
        static_url = f"/static/{os.path.basename(pdf_path['internal_path'])}"
        display_name = pdf_path["display_name"]


        # 분석 결과 저장
        db.add(FileAnalysis(
            analysis_id=analysis_id,
            user_id=user_id,
            filename=file.filename,
            file_size=f"{file_size_mb:.2f} MB",
            extension=ext,
            sha256=file_hash,
            result=result_label,
            #confidence=result_data.get("confidence"),
            confidence = float(confidence or 0.0),
            summary=summary,
            report_url=static_url,
            # normal=round(prob_data["normal"], 2),
            # malicious=round(prob_data["malicious"], 2),
            normal = float(round(prob_data.get("normal", 0.0), 2)),
            malicious = float(round(prob_data.get("malicious", 0.0), 2))
        ))

        # 로그 저장
        db.add(LogRecord(
            analysis_id=analysis_id,
            start_time=_parse_log_datetime(log_data.get("start_time")),
            model_load=log_data.get("model_load"),
            preprocess=log_data.get("preprocess"),
            inference=log_data.get("inference")
        ))

        # 모델 정보 저장
        db.add(ModelInfo(
            analysis_id=analysis_id,
            type=model_info.get("type"),
            input=model_info.get("input"),
            train_size=model_info.get("train_size"),
            test_accuracy=result_data.get("accuracy")
        ))

        # 성능 지표 저장
        db.add(PerformanceMetric(
            analysis_id=analysis_id,
            precision=model_performance.get("Precision"),
            recall=model_performance.get("Recall"),
            f1_score=model_performance.get("F1-Score"),
            benign_accuracy=model_performance.get("Benign"),
            malware_accuracy=model_performance.get("Malware")
        ))

        db.commit()

    # --- [4] 파일 삭제 ---
    # 분석 끝났으므로 원본 파일 삭제
    try:
        if os.path.exists(save_path):
            os.remove(save_path)
    except Exception as e:
        print(f"[파일 삭제 오류] {save_path} 제거 실패 → {e}")


    # --- [5] 결과 리턴 ---
    return {
        "analysis_id": str(analysis_id),
        "filename": file.filename,
        "file_size": file_size_str,
        "extension": f".{ext}",
        "sha256": file_hash,
        "log": {
            "start_time": log_data.get("start_time", "-"),
            "model_load": log_data.get("model_load", "-"),
            "preprocess": log_data.get("preprocess", "-"),
            "inference": log_data.get("inference", "-")
        },
        "normal": round(prob_data["normal"], 2),
        "malicious": round(prob_data["malicious"], 2),
        "result": result_label,
        "confidence": confidence,
        "summary": summary,
        "model_info": {
            "type": model_info.get("type", "Unknown"),
            "input": model_info.get("input", "-"),
            "train_size": model_info.get("train_size", "-"),
            "test_accuracy": result_data.get("accuracy")
        },
        "performance": {
            "Precision": model_performance.get("Precision"),
            "Recall": model_performance.get("Recall"),
            "F1-Score": model_performance.get("F1-Score"),
            "Benign Accuracy": model_performance.get("Benign"),
            "Malware Accuracy": model_performance.get("Malware")
        },
        "report_url": static_url if static_url else None,
        "display_name": display_name if display_name else None,

    }


    
