from pydantic import BaseModel


class InterviewQuestion(BaseModel):
    pergunta: str
    objetivo: str | None = None
    categoria: str


class InterviewQuestions(BaseModel):
    tecnicas: list[str] = []
    comportamentais: list[str] = []
    validacao_requisitos: list[str] = []
    armadilha: list[str] = []
