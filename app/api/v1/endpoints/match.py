# app/api/v1/endpoints/match.py
from fastapi import APIRouter, Depends
from app.schemas.match_schema import MatchRequest, MatchResponse
from app.services.ai_service import AIService
from app.dependencies import get_ai_service

router = APIRouter()


@router.post("/inteligente", response_model=MatchResponse)
async def match_inteligente(
    payload: MatchRequest,
    ai_service: AIService = Depends(get_ai_service)
):
    """Endpoint principal de análise inteligente de currículo"""
    return await ai_service.analisar_candidato(
        curriculo=payload.curriculo,
        vagas=payload.vagas
    )