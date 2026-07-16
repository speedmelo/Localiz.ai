# app/api/v1/endpoints/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user_schema import UserCreate, UserLogin, Token
from app.core.security import hash_password, verify_password, create_access_token
from app.database import get_db

router = APIRouter()


@router.post("/register", response_model=dict, status_code=201)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    # TODO: Integrar UserService completo
    return {"message": "Usuário criado com sucesso", "email": user.email}


@router.post("/login", response_model=Token)
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    # TODO: Buscar usuário real no banco
    if user.email == "admin@localiza.com" and user.password == "123456":
        token = create_access_token({"sub": user.email, "role": "recruiter"})
        return Token(access_token=token, token_type="bearer")
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas"
    )