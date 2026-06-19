# app/api/v1/router.py
from fastapi import APIRouter

# Importando todos os endpoints
from app.api.v1.endpoints import (
    auth,
    upload,
    match,
    interview,
    video,
    chat
)

# ====================== API PRINCIPAL v1 ======================
api_router = APIRouter(
    prefix="/api/v1",
    tags=["v1"],
    responses={
        404: {"description": "Não encontrado"},
        500: {"description": "Erro interno do servidor"}
    }
)

# ====================== INCLUSÃO DAS ROTAS ======================

# Auth (Cadastro e Login)
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])

# Upload de Currículos
api_router.include_router(upload.router, prefix="/upload", tags=["Upload"])

# Análise de Match com IA (Principal)
api_router.include_router(match.router, prefix="/match", tags=["Match IA"])

# Entrevistas
api_router.include_router(interview.router, prefix="/interview", tags=["Entrevistas"])

# Vídeo / Entrevista Online
api_router.include_router(video.router, prefix="/video", tags=["Vídeo"])

# Chat em Tempo Real
api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])


# ====================== DOCUMENTAÇÃO PERSONALIZADA ======================
api_router.tags_metadata = [
    {
        "name": "Auth",
        "description": "Autenticação de recrutadores e gestores de RH"
    },
    {
        "name": "Upload",
        "description": "Upload e extração de currículos em PDF"
    },
    {
        "name": "Match IA",
        "description": "Análise inteligente de compatibilidade entre candidato e vagas"
    },
    {
        "name": "Entrevistas",
        "description": "Agendamento e gestão de entrevistas"
    },
    {
        "name": "Vídeo",
        "description": "Geração de tokens para entrevistas por vídeo"
    },
    {
        "name": "Chat",
        "description": "Comunicação em tempo real via WebSocket"
    }
]