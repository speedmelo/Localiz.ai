from app.schemas.auth import LoginResponse, Token, TokenPayload
from app.schemas.user import UserCreate, UserLogin, UserResponse, UserUpdate
from app.schemas.candidate import (
    CandidateAnalysisRequest,
    CandidateComparisonRequest,
    CandidateUploadResponse,
)
from app.schemas.vacancy import VacancyCreate, VacancyRequirement, VacancyResponse
from app.schemas.match import MatchRequest, MatchResponse
from app.schemas.interview import InterviewQuestion, InterviewQuestions
from app.schemas.geolocation import CandidateLocation, NearbyVacancy
from app.schemas.ai import (
    AIAnalysisResponse,
    AIRankingItem,
    AIRequirementStatus,
)
from app.schemas.response import APIResponse, ErrorResponse

__all__ = [
    "LoginResponse",
    "Token",
    "TokenPayload",
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "UserUpdate",
    "CandidateAnalysisRequest",
    "CandidateComparisonRequest",
    "CandidateUploadResponse",
    "VacancyCreate",
    "VacancyRequirement",
    "VacancyResponse",
    "MatchRequest",
    "MatchResponse",
    "InterviewQuestion",
    "InterviewQuestions",
    "CandidateLocation",
    "NearbyVacancy",
    "AIAnalysisResponse",
    "AIRankingItem",
    "AIRequirementStatus",
    "APIResponse",
    "ErrorResponse",
]
