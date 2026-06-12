## app/api/endpoints/reports_legacy.py
from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import FileResponse
import json
from app.services.reports import generate_final_pdf_report
from datetime import datetime
import torch
import os

router = APIRouter()

# 확장자별 기본 모델 정보 정리 -> 확장자 추가 시 유지 보수 편함
MODEL_INFO_MAP = {
    "exe": {
        "type": "CNN",
        "input": "Grayscale, 256x256",
        "train_size": "20,000"
    },
    "pdf": {
        "type": "CNN",
        "input": "Grayscale, 256x256",
        "train_size": "18,000"
    },
    "hwp": {
        "type": "CNN",
        "input": "Grayscale, 256x256",
        "train_size": "19,000"
    },
    
}

# 모델 정보 자동 추출 함수 (없을 경우 기본값을 명시적으로 제공)
def extract_model_info(extension: str):
    ext = extension.lower()
    model_path = os.path.join(os.path.dirname(__file__), f"../../assets/CNN_{ext}.pth")

    ## 확장자 구분 못할 시, 또는 없을 시 넣는 더미 값 (Unknown)
    default_info = MODEL_INFO_MAP.get(ext, {
        "type": "Unknown",
        "input": "Unknown",
        "train_size": "Unknown"
    })

    if not os.path.exists(model_path):
        return default_info

    try:
        checkpoint = torch.load(model_path, map_location="cpu")
        num_classes = checkpoint.get("num_classes")

        return {
            "type": default_info["type"],
            "input": default_info["input"],
            "train_size": f"{num_classes * 10000:,}" if isinstance(num_classes, int) else default_info["train_size"]
        }

    except Exception as e:
        print(f"모델 정보 추출 실패: {e}")
        return default_info


@router.post("/report/download")
def download_pdf_report(
    file: UploadFile = File(...),
    result: str = Form(...)
):
    """
    file: 업로드한 파일
    result: /predict 와 /piechart 결과를 포함하는 JSON 문자열

    출력 result JSON 예시:
    {
        "confidence": 0.87,
        "accuracy": 95.61,
        "result": "악성",
        "log": {
            "start_time": "2025/04/07 14:22:10",
            "model_load": 0.91,
            "preprocess": 0.72,
            "inference": 1.07
        },
        "model_info": {  # 없으면 아래에서 자동 삽입
            "type": "CNN",
            "input": "Grayscale, 256x256",
            "train_size": "20,000"
        }
    }
    """
    result_dict = json.loads(result)

    # model_info 자동 추출 (없으면 추정 또는 기본값)
    extension = file.filename.split(".")[-1].lower()
    if "model_info" not in result_dict:
        result_dict["model_info"] = extract_model_info(extension)

    # log 자동 채우기 (없을 경우 현재 시간 기반으로)
    if "log" not in result_dict or not isinstance(result_dict["log"], dict):
        result_dict["log"] = {
            "start_time": datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
            "model_load": "-",
            "preprocess": "-",
            "inference": "-"
        }

    pdf_path = generate_final_pdf_report(file, result_dict)
    return FileResponse(
        path=pdf_path,
        filename=f"{file.filename}_report.pdf",
        media_type="application/pdf"
    )
