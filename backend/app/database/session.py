# # 혹시 몰라 만들어둔 데베 -> 사용 안할 시 삭제 가능
# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
# from app.core.config import settings

# engine = create_engine(
#     settings.DATABASE_URL,
#     connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
# )
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()
