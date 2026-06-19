from pydantic import BaseModel, Field


class CandidateLocation(BaseModel):
    endereco: str = Field(min_length=5)


class NearbyVacancy(BaseModel):
    nome: str
    endereco: str
    descricao: str = ""
    distancia_km: float = Field(ge=0)
