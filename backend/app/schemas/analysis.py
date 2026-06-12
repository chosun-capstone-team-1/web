# app/schemas/analysis.py -> Pydantic 스키마, API 응답용 모델
from pydantic import BaseModel
from datetime import datetime

class FileAnalysisResponse(BaseModel):
    analysis_id: str
    filename: str
    result: str
    malicious_ratio: float
    uploaded_at: datetime
    report_url: str

    class Config:
        orm_mode = True
