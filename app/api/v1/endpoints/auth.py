# app/api/v1/endpoints/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.user_schema import UserCreate, Token
from app.core.security import hash_password, verify_password, create_access_token
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.post("/register", response_model=dict, status_code=201)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    # TODO: Integrar com UserService + verificar email duplicado
    return {"message": "Usuário criado com sucesso", "email": user.email}


@router.post("/login", response_model=Token)
async def login(user: UserCreate, db: AsyncSession = Depends(get_db)):
    # TODO: Implementar busca real no banco + verify_password
    token = create_access_token({"sub": user.email, "role": "recruiter"})
    return Token(access_token=token, token_type="bearer")