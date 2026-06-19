from pydantic import BaseModel, Field

from app.schemas.vacancy import VacancyCreate


class MatchRequest(BaseModel):
    curriculo: str = Field(min_length=50)
    vagas: list[VacancyCreate] = Field(min_length=1)


class MatchResponse(BaseModel):
    melhor_vaga: str
    score: int = Field(ge=0, le=100)
    risco_contratacao: str
    parecer_executivo: str
