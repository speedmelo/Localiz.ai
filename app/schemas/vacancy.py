from pydantic import BaseModel, Field


class VacancyRequirement(BaseModel):
    description: str
    required: bool = True
    weight: int = Field(default=10, ge=0, le=100)


class VacancyCreate(BaseModel):
    nome: str = Field(min_length=2, max_length=120)
    descricao: str = Field(min_length=10)
    requisitos: list[VacancyRequirement] = []


class VacancyResponse(BaseModel):
    nome: str
    descricao: str
    requisitos: list[VacancyRequirement] = []
