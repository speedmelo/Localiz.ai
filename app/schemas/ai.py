from pydantic import BaseModel, Field


class AIRequirementStatus(BaseModel):
    requisito: str
    status: str
    evidencia: str | None = None


class AIRankingItem(BaseModel):
    vaga: str
    score_aderencia: int = Field(ge=0, le=100)
    classificacao: str
    pontos_fortes: list[str] = []
    pontos_fracos: list[str] = []
    requisitos_atendidos: list[str] = []
    requisitos_nao_atendidos: list[str] = []
    requisitos_nao_identificados: list[str] = []
    justificativa: str = ""


class AIAnalysisResponse(BaseModel):
    melhor_vaga: str
    ranking_vagas: list[AIRankingItem]
    nivel_candidato: str
    risco_contratacao: str
    red_flags: list[str] = []
    perguntas_entrevista: dict
    parecer_executivo: str
    recomendacao_final: str
