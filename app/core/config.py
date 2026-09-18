import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
	openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
	openai_model: str = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")
	upload_folder: str = os.getenv("UPLOAD_FOLDER", "documents/uploads")
	embedding_model: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
	retrieval_top_k: int = int(os.getenv("RETRIEVAL_TOP_K", "3"))
	max_validation_retries: int = int(os.getenv("MAX_VALIDATION_RETRIES", "1"))


settings = Settings()

# Keep these names for existing service consumers.
OPENAI_API_KEY = settings.openai_api_key
OPENAI_MODEL = settings.openai_model