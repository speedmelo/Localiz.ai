# app/api/v1/router.py
from fastapi import APIRouter

# Importando os endpoints
from app.api.v1.endpoints import auth

api_router = APIRouter()

# Incluindo as rotas
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])