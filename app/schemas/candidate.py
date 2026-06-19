from pydantic import BaseModel, Field


class CandidateAnalysisRequest(BaseModel):
    curriculo: str = Field(min_length=50, description="Texto extraído do currículo")


class CandidateComparisonRequest(BaseModel):
    curriculos: list[str] = Field(
        min_length=1,
        max_length=3,
        description="Lista com 1 a 3 currículos para comparação",
    )


class CandidateUploadResponse(BaseModel):
    filename: str
    extracted_text_length: int
    status: str = "processed"
