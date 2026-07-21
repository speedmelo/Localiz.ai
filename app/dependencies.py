# app/dependencies.py
from app.services.ai_service import AIService

def get_ai_service() -> AIService:
    """
    Retorna a instância do serviço de IA para ser injetado nos endpoints do FastAPI.
    """
    return AIService()