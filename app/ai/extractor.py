import os
from typing import Any

from google import genai
from google.genai import types

from app.ai.parser import safe_json_parse, sanitize_resume_text
from app.ai.prompts import build_candidate_evidence_prompt
from app.core.logging import get_logger

logger = get_logger("ai_extractor")


GEMINI_MODEL = "gemini-2.5-flash"


def get_gemini_client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError("GEMINI_API_KEY não configurada no .env")

    return genai.Client(api_key=api_key)


async def extract_candidate_evidence(curriculo_texto: str) -> dict[str, Any]:
    """
    Extrai evidências do currículo usando Gemini.

    Importante:
    - Não calcula score final.
    - Não decide contratação.
    - Apenas estrutura evidências para as engines.
    """

    cleaned_resume = sanitize_resume_text(curriculo_texto)

    if not cleaned_resume:
        raise ValueError("Currículo vazio ou inválido.")

    prompt = build_candidate_evidence_prompt(cleaned_resume)
    client = get_gemini_client()

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1,
            ),
        )

        result = safe_json_parse(response.text or "")

        logger.info("Evidências extraídas com sucesso pela IA.")

        return result

    except Exception as exc:
        logger.exception("Erro ao extrair evidências com Gemini.")
        return {
            "erro": "Erro ao extrair evidências do currículo",
            "detalhe": str(exc),
        }
