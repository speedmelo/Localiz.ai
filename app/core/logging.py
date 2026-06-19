# app/core/logging.py
import logging
import sys
from pathlib import Path
from typing import Optional

import structlog  # Recomendado (mais moderno e bonito)


def configure_logging(
    level: int = logging.INFO,
    log_to_file: bool = False,
    log_dir: str = "logs"
) -> None:
    """
    Configuração profissional de logging para ambiente enterprise.
    Suporta structlog (recomendado) ou logging nativo.
    """
    
    # Cria pasta de logs se necessário
    if log_to_file:
        Path(log_dir).mkdir(exist_ok=True)

    # Configuração básica do logging nativo
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
        force=True
    )

    # Configuração do structlog (mais bonito e estruturado)
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.JSONRenderer() if not log_to_file else structlog.dev.ConsoleRenderer(),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Reduz ruído de bibliotecas externas
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)

    # Logger principal da aplicação
    logger = logging.getLogger("app")
    logger.setLevel(level)

    if log_to_file:
        file_handler = logging.FileHandler(f"{log_dir}/app.log", encoding="utf-8")
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")
        )
        logger.addHandler(file_handler)

    logger.info(f"🚀 Logging configurado com nível {logging.getLevelName(level)}")


# Função de conveniência para obter logger
def get_logger(name: str = "app"):
    return structlog.get_logger(name)