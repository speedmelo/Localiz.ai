# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
from pathlib import Path


class Settings(BaseSettings):
    """
    Configurações da aplicação usando Pydantic Settings (melhor prática 2026).
    Lê automaticamente o arquivo .env na raiz do projeto.
    """

    model_config = SettingsConfigDict(
        env_file=".env",           # Procura automaticamente na raiz
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",            # Ignora variáveis não declaradas
        env_ignore_empty=True
    )

    # ==================== APLICAÇÃO ====================
    PROJECT_NAME: str = "Localiz.ai - Talent Intelligence"
    VERSION: str = "2.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"  # development, staging, production

    # ==================== BANCO DE DADOS ====================
    DATABASE_URL: str

    # ==================== SEGURANÇA ====================
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440   # 24 horas
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ==================== FRONTEND ====================
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ]

    # ==================== INTELIGÊNCIA ARTIFICIAL ====================
    OPENAI_API_KEY: str | None = None
    GROK_API_KEY: str | None = None
    MODEL_NAME: str = "gpt-4o-mini"          # ou "grok-beta", etc.
    MAX_TOKENS_ANALISE: int = 4000

    # ==================== OUTROS ====================
    UPLOAD_MAX_SIZE_MB: int = 10
    RATE_LIMIT_PER_MINUTE: int = 30


# Instância global
settings = Settings()