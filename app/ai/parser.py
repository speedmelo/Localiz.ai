import json
import re
from typing import Any

from app.core.logging import get_logger

logger = get_logger("ai_parser")


MAX_RESUME_TEXT_LENGTH = 60_000


def sanitize_resume_text(text: str) -> str:
    """
    Limpa o texto do currículo antes de enviar para a IA.
    """

    if not text:
        return ""

    cleaned = text.replace("\x00", " ")
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    return cleaned[:MAX_RESUME_TEXT_LENGTH]


def safe_json_parse(text: str) -> dict[str, Any]:
    """
    Extrai JSON de uma resposta da IA de forma robusta.
    """

    if not text:
        return {
            "erro": "Resposta vazia da IA",
            "resposta_bruta": text,
        }

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    json_match = re.search(r"\{.*\}", text, re.DOTALL)

    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            logger.warning("JSON encontrado, mas inválido.")

    logger.warning("Falha ao interpretar JSON retornado pela IA.")

    return {
        "erro": "Falha ao interpretar resposta da IA",
        "resposta_bruta": text,
    }
