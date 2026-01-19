from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str
    DATABASE_URL: str = "qwe"


    OPENAI_API_KEY: str

    MIN_SCRIPT_NAME_LENGTH: int = 3
    MAX_SCRIPT_NAME_LENGTH: int = 7
    REPEAT_SCRIPT_NAME_GENERATE: int = 3
    IF_SCRIPT_NAME_EXISTS: int = 10
    NAME_CHOICES: str = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM0987654321"
    SCRIPT_ACTIVE_TIME_MINUTES: int = 120
    MIN_FINGERPRINT_LEN: int = 8

    UPLOAD_PATH: str = "answers"

    AUTH_TOKENS: list = ["qwe"] #BACKEND_API_KEYs

    def model_post_init(self, __context):
        self.DATABASE_URL = (
            f"postgres://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()