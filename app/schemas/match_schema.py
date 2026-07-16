# app/schemas/match_schema.py
from pydantic import BaseModel
from typing import Any, Dict, List, Optional

class MatchRequest(BaseModel):
    curriculo: str
    vagas: List[Dict[str, Any]]

class MatchResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    processing_time_ms: Optional[float] = None
    model_version: Optional[str] = None
    request_id: Optional[str] = None