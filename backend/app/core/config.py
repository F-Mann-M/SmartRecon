from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings): # load all key=value pairs from .env
    """ Load Database"""
    DATABASE_URL: str = f"postgresql+psycopg://postgres:postgrespassword@localhost:5432/smartrecon"

    """Load RAW PDF"""
    RAW_INVOICE_DIR: str = f"{BASE_DIR}/data/raw/invoices"
    RAW_STATEMENTS_DIR: str = f"{BASE_DIR}/data/raw/statements"  

    model_config = SettingsConfigDict(
        env_file = BASE_DIR/".env",
        env_file_encoding = "utf-8",
    )

settings = Settings()