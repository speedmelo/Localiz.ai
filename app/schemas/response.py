from typing import Any

from pydantic import BaseModel


class APIResponse(BaseModel):
    success: bool = True
    message: str | None = None
    data: Any | None = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    detail: str | None = None
