# app/dependencies.py
from app.services.ai_service import AIService

def get_ai_service():
    """
    Retorna o método de análise da IA para ser injetado nos endpoints do FastAPI.
    """
    return AIService.analisar_candidato