import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class Settings:
    PORT: int = int(os.getenv("PORT", "8000"))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    
    # AI Provider settings
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "gemini").lower()
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # AI4Bharat / Indian Language API settings
    AI4BHARAT_API_KEY: str = os.getenv("AI4BHARAT_API_KEY", "")
    AI4BHARAT_ENDPOINT: str = os.getenv("AI4BHARAT_ENDPOINT", "https://api.dhruva.ai4bharat.org")

    # Paths
    BASE_DIR: Path = BASE_DIR
    DATA_DIR: Path = BASE_DIR / "data"
    DB_PATH: Path = BASE_DIR / "trustlens.db"
    
    @property
    def has_ai4bharat(self) -> bool:
        return bool(self.AI4BHARAT_API_KEY and self.AI4BHARAT_API_KEY.strip())
    
    @property
    def has_gemini(self) -> bool:
        return bool(self.GEMINI_API_KEY and self.GEMINI_API_KEY.strip())
        
    @property
    def has_openai(self) -> bool:
        return bool(self.OPENAI_API_KEY and self.OPENAI_API_KEY.strip())

    @property
    def is_ai_enabled(self) -> bool:
        return self.has_gemini or self.has_openai

settings = Settings()

