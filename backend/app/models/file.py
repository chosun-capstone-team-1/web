# # 혹시 몰라 만들어둔 데베 -> 사용 안할 시 삭제 가능
# from sqlalchemy import Column, Integer, String, DateTime
# from datetime import datetime
# from app.database.session import Base

# class File(Base):
#     __tablename__ = "files"
#     id = Column(Integer, primary_key=True, index=True)
#     filename = Column(String, unique=True, index=True)
#     path = Column(String)
#     prediction = Column(String)
#     created_at = Column(DateTime, default=datetime.utcnow)
