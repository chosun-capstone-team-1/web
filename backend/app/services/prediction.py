## app/services/prediction.py
import os

import torch
from torchvision import transforms

from app.models.cnn_model import ExeCNN_AdaptiveAvgPool_Dropout, SimpleCNN
from app.models.rf_model import RandomForestPDFModel
from app.models.auto_encoder_model import AEWithClassifier
from app.utils.file_processing import CONVERTER_MAP
from app.utils.performance_timer import InferenceTimer


MODEL_CACHE = {}
BACKEND_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
MODEL_DIRS = [
    os.path.join(BACKEND_ROOT, "models"),      # required production path: backend/models/CNN_exe.pth
    os.path.join(BACKEND_ROOT, "app", "assets"),  # legacy fallback path
]

# 정확도 맵 (하드코딩 값은 향후 동적 추출로 확장 가능)
ACCURACY_MAP = {
    "exe": 95.61,
    "pdf": 93.42,
    "hwp": 94.00,
    "docx": 79.00,
    "xlsx": 76.00,
}

PREFERRED_MODEL_FILENAMES = {
    "exe": ["CNN_exe.pth"],
    "pdf": ["Randomforest_pdf.pkl"],
}


def _available_model_dirs():
    return [model_dir for model_dir in MODEL_DIRS if os.path.isdir(model_dir)]


def _find_model_path(ext: str):
    model_dirs = _available_model_dirs()
    for filename in PREFERRED_MODEL_FILENAMES.get(ext, []):
        for model_dir in model_dirs:
            candidate = os.path.join(model_dir, filename)
            if os.path.exists(candidate):
                return candidate

    for suffix in [".pth", ".pkl"]:
        for model_dir in model_dirs:
            for filename in os.listdir(model_dir):
                if filename.endswith(suffix) and f"_{ext}" in filename:
                    return os.path.join(model_dir, filename)
    return None


def _extract_checkpoint_state(checkpoint):
    if isinstance(checkpoint, dict):
        if "model_state_dict" in checkpoint:
            return checkpoint["model_state_dict"], checkpoint.get("num_classes", 2)
        if "state_dict" in checkpoint:
            return checkpoint["state_dict"], checkpoint.get("num_classes", 2)
    return checkpoint, 2


def _load_state_with_fallback(model_path: str, ext: str):
    checkpoint = torch.load(model_path, map_location="cpu")
    state_dict, num_classes = _extract_checkpoint_state(checkpoint)

    candidates = []
    if ext == "exe":
        candidates.append(ExeCNN_AdaptiveAvgPool_Dropout(num_classes=num_classes))
    candidates.append(SimpleCNN(num_classes))

    errors = []
    for model in candidates:
        try:
            model.load_state_dict(state_dict)
            model.eval()
            return model
        except Exception as exc:
            errors.append(f"{model.__class__.__name__}: {exc}")

    raise RuntimeError(
        "모델 구조와 체크포인트가 일치하지 않습니다. "
        f"시도한 구조: {' | '.join(errors)}"
    )


# CNN + RandomForest + Auto Encoder 모델 로딩 통합
def load_model_by_extension(file_ext: str):
    ext = file_ext.strip(".").lower()
    if ext not in MODEL_CACHE:
        model_path = _find_model_path(ext)
        if not model_path:
            expected = os.path.join(BACKEND_ROOT, "models", PREFERRED_MODEL_FILENAMES.get(ext, [f"*_{ext}.*"])[0])
            raise FileNotFoundError(
                f"{ext} 확장자에 맞는 모델 파일을 찾을 수 없습니다. "
                f"필요 경로: {expected}"
            )

        # AEWithClassifier 모델인 경우 (state_dict만 저장됨)
        if ext in ["hwp", "xlsx", "docx"] and model_path.endswith(".pth"):
            model = AEWithClassifier()
            model.load_state_dict(torch.load(model_path, map_location="cpu"))
            model.eval()

        # CNN 모델인 경우 (exe 등)
        elif model_path.endswith(".pth"):
            model = _load_state_with_fallback(model_path, ext)

        # RandomForest 모델인 경우 (pdf 등)
        elif model_path.endswith(".pkl"):
            model = RandomForestPDFModel(model_path)

        else:
            raise ValueError(f"지원하지 않는 모델 형식: {model_path}")

        MODEL_CACHE[ext] = model

    return MODEL_CACHE[ext]


def _image_transform(resize_shape):
    return transforms.Compose([
        transforms.Grayscale(num_output_channels=1),
        transforms.Resize(resize_shape),
        transforms.ToTensor(),
        transforms.Normalize((0.5,), (0.5,)),
    ])


def _run_prediction(file_path: str, file_ext: str):
    ext = file_ext.lower().strip(".")
    timer = InferenceTimer()
    model = load_model_by_extension(ext)
    timer.mark("model_load")

    if ext not in CONVERTER_MAP:
        raise ValueError(f"{ext} 확장자는 아직 지원되지 않습니다.")
    convert_func, resize_shape = CONVERTER_MAP[ext]
    data = convert_func(file_path)
    timer.mark("preprocess")

    if isinstance(model, (SimpleCNN, ExeCNN_AdaptiveAvgPool_Dropout, AEWithClassifier)):
        input_tensor = _image_transform(resize_shape)(data).unsqueeze(0)
        with torch.no_grad():
            if isinstance(model, AEWithClassifier):
                _, logits = model(input_tensor)
            else:
                logits = model(input_tensor)
            probs = torch.nn.functional.softmax(logits, dim=1)[0]
            prediction = torch.argmax(logits, 1).item()
            normal_score = round(probs[0].item() * 100, 2)
            malicious_score = round(probs[1].item() * 100, 2)
    else:
        prediction, proba = model.predict(data)
        normal_score = round(proba[0] * 100, 2)
        malicious_score = round(proba[1] * 100, 2)

    timer.mark("inference")
    return prediction, normal_score, malicious_score, timer


# 악성/정상 판단 함수 (CNN or RF or AE 공통 처리)
def predict(file_path: str, file_ext: str):
    ext = file_ext.lower().strip(".")
    try:
        prediction, _, _, timer = _run_prediction(file_path, ext)
        result = "악성" if prediction == 1 else "정상"  # class mapping: Benign=0, Malware=1
        accuracy = ACCURACY_MAP.get(ext, None)
    except Exception as e:
        timer = InferenceTimer()
        result = f"에러 발생: {str(e)}"
        accuracy = None

    return {
        "result": result,
        "accuracy": accuracy,
        "log": timer.get_log()
    }


# 확률 반환 함수 (CNN & RandomForest & AE 모두 대응)
def predict_probabilities(file_path: str, file_ext: str):
    ext = file_ext.lower().strip(".")
    try:
        _, normal_score, malicious_score, _ = _run_prediction(file_path, ext)
    except Exception as e:
        normal_score, malicious_score = 0.0, 0.0
        print(f"에러 발생: {str(e)}")

    return {
        "normal": normal_score,
        "malicious": malicious_score
    }


# 전체 보고서 출력용 데이터
def predict_full_report_data(file_path: str, file_ext: str):
    ext = file_ext.lower().strip(".")
    try:
        prediction, normal_score, malicious_score, timer = _run_prediction(file_path, ext)
        result = "악성" if prediction == 1 else "정상"
        accuracy = ACCURACY_MAP.get(ext, None)
    except Exception as e:
        timer = InferenceTimer()
        result = f"에러 발생: {str(e)}"
        accuracy = None
        normal_score, malicious_score = 0.0, 0.0

    return (
        {
            "result": result,
            "accuracy": accuracy,
            "log": timer.get_log()
        },
        {
            "normal": normal_score,
            "malicious": malicious_score
        }
    )
