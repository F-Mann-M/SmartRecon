from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from typing import Literal
import os

APP_ENV = os.getenv("APP_ENV", "cloud")  # "local" or "cloud"
ENV_FILE = f".env.{APP_ENV}"
BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings): 
    """ Application settings loaded from environment variables and .env file """
    ENVIRONMENT: Literal["local", "cloud"] = "local"

    # Cloud / Azure Foundry Settings
    AZURE_OPENAI_ENDPOINT: str | None = None
    AZURE_CLIENT_ID: str | None = None  # User-Assigned Managed Identity client ID
    AZURE_OPENAI_API_VERSION: str = "2025-08-07"
    AZURE_DEPLOYMENT_CHAT: str = "gpt-5-mini"
    AZURE_DEPLOYMENT_EMBEDDING: str = "text-embedding-3-small"
    AZURE_EMBEDDING_API_VERSION: str = "2024-02-01"

    # Local Models Settings (Direct Ollama)
    LOCAL_CHAT_MODEL: str = "gemma2:9b"
    LOCAL_EMBEDDING_MODEL: str = "embeddinggemma"
    LOCAL_STRUCTURED_MODEL: str = "llama3.1:8b"

    # Local Database Settings
    DATABASE_URL: str = f"postgresql+psycopg://postgres:postgrespassword@localhost:5432/smartrecon"

    RAW_INVOICE_DIR: str = f"{BASE_DIR}/data/raw/invoices"
    RAW_STATEMENT_DIR: str = f"{BASE_DIR}/data/raw/bank_statements" 
    
    # Cloud Storage Settings (Azure Blob Storage)
    AZURE_STORAGE_CONNECTION_STRING: str | None = None

    model_config = SettingsConfigDict(
        env_file = ENV_FILE,
        env_file_encoding = "utf-8",
        extra="ignore",
    )

settings = Settings() 