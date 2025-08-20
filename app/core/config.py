from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    google_api_key: str
    faiss_dir: str = "data/faiss"
    model_name: str = "all-MiniLM-L6-v2"
    DATABASE_URL: str
    openai_api_key: str  
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region: str
    artwork_s3_bucket_name: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

settings = Settings()