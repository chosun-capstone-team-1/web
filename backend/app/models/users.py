# # 혹시 몰라 만들어둔 데베 -> 사용 안할 시 삭제 가능
# from sqlalchemy import Column, Integer, String
# from app.database.session import Base

# class User(Base):
#     __tablename__ = "users"
#     id = Column(Integer, primary_key=True, index=True)
#     username = Column(String, unique=True, index=True)
#     email = Column(String, unique=True, index=True)
#     hashed_password = Column(String)
