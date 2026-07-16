# app/schemas/__init__.py

# Importações dos schemas
from app.schemas.user_schema import UserCreate, UserLogin, Token, UserResponse
from app.schemas.candidate import (
    CandidateAnalysisRequest,
    CandidateComparisonRequest,
    CandidateUploadResponse,
)
from app.schemas.match_schema import MatchRequest, MatchResponse
# Adicione outros schemas conforme for criando

__all__ = [
    "UserCreate",
    "UserLogin",
    "Token",
    "UserResponse",
    "CandidateAnalysisRequest",
    "CandidateComparisonRequest",
    "CandidateUploadResponse",
    "MatchRequest",
    "MatchResponse",
]