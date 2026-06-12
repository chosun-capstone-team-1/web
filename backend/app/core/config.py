# # 혹시 몰라 만들어둔 데베 -> 사용 안할 시 삭제 가능
# from pydantic import BaseSettings

# class Settings(BaseSettings):
#     DATABASE_URL: str = "sqlite:///./test.db"
#     SECRET_KEY: str = "your_secret_key"
#     ALGORITHM: str = "HS256"
#     ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

#     class Config:
#         env_file = ".env"

# settings = Settings()
