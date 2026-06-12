## app/api/endpoints/files.py
from fastapi import APIRouter, UploadFile, File
import os
import shutil
import uuid
from datetime import datetime
import pytz
import hashlib
from app.services.prediction import ACCURACY_MAP
from app.services.prediction import predict, predict_probabilities
from app.utils.model_info import extract_model_info, get_model_performance_score

router = APIRouter()

INPUT_DIR = "./temp_uploads/input"
os.makedirs(INPUT_DIR, exist_ok=True)

def get_safe_path(filename: str) -> tuple[str, str]:
    ext = os.path.splitext(filename)[1]
    unique_filename = f"{uuid.uuid4().hex}{ext}" ## 한글 파일 명 깨지는 충돌 완화
    return os.path.join(INPUT_DIR, unique_filename), unique_filename

## 파일 악성/정상 판별 + 모델의 정확도
@router.post("/predict")
async def predict_file(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1]
    save_path = os.path.join(INPUT_DIR, file.filename) 
    #save_path = f"./temp_uploads/{file.filename}"
    os.makedirs(INPUT_DIR, exist_ok=True)

    try:
        contents = await file.read()
        with open(save_path, "wb") as f:
            f.write(contents)

        file_hash = hashlib.sha256(contents).hexdigest()
        file_size_mb = len(contents) / 1024 / 1024
        file_size_str = f"{file_size_mb:.2f} MB"

        prediction_result = predict(save_path, ext)
        return {
            "filename": file.filename,
            "file_size": file_size_str,
            "extension": ext,
            "sha256": file_hash,
            #"result": prediction_result["result"],
            #"accuracy": prediction_result["accuracy"],
            "log": prediction_result["log"]
        }
    except Exception as e:
        return {"error": str(e)}


## Pie Chart : 파일 악성/정상 몇 % 비율인지
@router.post("/piechart")
async def predict_piechart(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1]
    save_path = os.path.join(INPUT_DIR, file.filename) 
    #save_path = f"./temp_uploads/{file.filename}"
    os.makedirs(INPUT_DIR, exist_ok=True)

    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        result = predict_probabilities(save_path, ext)
        malicious_percent = result["malicious"]
        result_label = "악성" if malicious_percent >= 60 else "정상"
        summary = f"해당 \"{file.filename}\" 파일은 {result_label}으로 탐지되었으며, {malicious_percent:.1f}%의 탐지 확률을 기반으로 판단됩니다."

        # 모델 정확도 정보
        confidence = ACCURACY_MAP.get(ext.strip('.').lower(), None)
        
        return {
            "filename": file.filename,
            "normal": result["normal"],
            "malicious": result["malicious"],
            "result": result_label,
            "confidence": confidence,
            "summary": summary
        }
    except Exception as e:
        return {"error": str(e)}
    
## 분석 환경 + 분석 로그 요약
@router.post("/meta")
async def extract_file_meta(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1]
    save_path = os.path.join(INPUT_DIR, file.filename) 
    #save_path = f"./temp_uploads/{file.filename}"
    os.makedirs(INPUT_DIR, exist_ok=True)
    performance = get_model_performance_score(ext)

    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        # 분석 결과 예측 (여기서 log 포함돼서 나옴)
        result = predict(save_path, ext)
        log = result.get("log", {})
        model_info = extract_model_info(ext)

        return {
            "model_info": {
                "type": model_info.get("type", "Unknown"),
                "input": model_info.get("input", "-"),
                "train_size": model_info.get("train_size", "-"),
                "test_accuracy": result.get("accuracy", None)
            },
            "log": {
                "start_time": log.get("start_time", "-"),
                "model_load": log.get("model_load", "-"),
                "preprocess": log.get("preprocess", "-"),
                "inference": log.get("inference", "-")
            },
            "performance": {
                "Precision": performance.get("Precision"),
                "Recall": performance.get("Recall"),
                "F1-Score": performance.get("F1-Score"),
                "Benign Accuracy": performance.get("Benign"),
                "Malware Accuracy": performance.get("Malware")
            }
        }

    except Exception as e:
        return {"error": str(e)}
