# app/db_persistence/analysis.py -> analyze-full API 값을 DB에 분석 결과 저장
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text, REAL, Integer
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.declarative import declarative_base
import uuid
from datetime import datetime

Base = declarative_base()

class FileAnalysis(Base):
   __tablename__ = "analyses"

   analysis_id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
   user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
   filename = Column(Text, nullable=False)
   file_size = Column(Text)
   extension = Column(Text)
   sha256 = Column(Text)
   result = Column(Text)
   confidence = Column(REAL)
   summary = Column(Text)
   report_url = Column(Text)
   normal = Column(REAL)
   malicious = Column(REAL)
   created_at = Column(DateTime, default=datetime.utcnow)
   

class LogRecord(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_id = Column(PG_UUID(as_uuid=True), ForeignKey("analyses.analysis_id", ondelete="CASCADE"))
    start_time = Column(DateTime)
    model_load = Column(REAL)
    preprocess = Column(REAL)
    inference = Column(REAL)

    
class ModelInfo(Base):
   __tablename__ = "model_infos"

   id = Column(Integer, primary_key=True, autoincrement=True)
   analysis_id = Column(PG_UUID(as_uuid=True), ForeignKey("analyses.analysis_id", ondelete="CASCADE"))
   type = Column(Text)
   input = Column(Text)
   train_size = Column(Text)
   test_accuracy = Column(REAL)


class PerformanceMetric(Base):
    __tablename__ = "performance_metrics"
    id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_id = Column(PG_UUID(as_uuid=True), ForeignKey("analyses.analysis_id", ondelete="CASCADE"))
    precision = Column(REAL)
    recall = Column(REAL)
    f1_score = Column(REAL)
    benign_accuracy = Column(REAL)
    malware_accuracy = Column(REAL)