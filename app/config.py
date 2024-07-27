# app/core/config.py

import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()  # Take environment variables from .env.

class Settings(BaseSettings):
    MONGO_URI: str
    MONGO_DB: str = "NextStepCareer"  # Default value if not set
    OPENAI_API_KEY: str
    UPLOAD_FOLDER: str = os.getenv("UPLOAD_FOLDER", "uploads")
    ALLOWED_EXTENSIONS: set = {'pdf', 'doc', 'docx'}

    class Config:
        # Tells Pydantic to read the environment variables.
        env_file = ".env"
        extra = "ignore"


settings = Settings()

# Debugging print statements
print(f"MONGO_URI: {settings.MONGO_URI}")
print(f"MONGO_DB: {settings.MONGO_DB}")
print(f"OPENAI_API_KEY: {settings.OPENAI_API_KEY}")
print(f"UPLOAD_FOLDER: {settings.UPLOAD_FOLDER}")
print(f"ALLOWED_EXTENSIONS: {settings.ALLOWED_EXTENSIONS}")
