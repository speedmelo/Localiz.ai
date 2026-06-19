from pydantic import BaseModel
from typing import List

class Vaga(BaseModel):
    nome: str
    descricao: str

class MatchRequest(BaseModel):
    curriculo: str
    vagas: List[Vaga]