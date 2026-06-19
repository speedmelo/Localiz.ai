from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash, verify_password
from app.models.user import User


class UserService:
    """
    Serviço responsável pelas regras de negócio de usuários.

    Mantém a lógica de usuário fora das rotas e evita acesso direto ao banco
    dentro dos endpoints.
    """

    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        user_id: int,
    ) -> User | None:
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_email(
        db: AsyncSession,
        email: str,
    ) -> User | None:
        normalized_email = email.strip().lower()

        result = await db.execute(
            select(User).where(User.email == normalized_email)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create_user(
        db: AsyncSession,
        email: str,
        password: str,
    ) -> User:
        normalized_email = email.strip().lower()

        existing_user = await UserService.get_by_email(
            db=db,
            email=normalized_email,
        )

        if existing_user:
            raise ValueError("Já existe um usuário cadastrado com este e-mail.")

        user = User(
            email=normalized_email,
            password_hash=get_password_hash(password),
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)

        return user

    @staticmethod
    async def authenticate_user(
        db: AsyncSession,
        email: str,
        password: str,
    ) -> User | None:
        user = await UserService.get_by_email(
            db=db,
            email=email,
        )

        if not user:
            return None

        if not verify_password(password, user.password_hash):
            return None

        return user

    @staticmethod
    async def update_password(
        db: AsyncSession,
        user_id: int,
        new_password: str,
    ) -> User:
        user = await UserService.get_by_id(
            db=db,
            user_id=user_id,
        )

        if not user:
            raise ValueError("Usuário não encontrado.")

        user.password_hash = get_password_hash(new_password)

        await db.commit()
        await db.refresh(user)

        return user

    @staticmethod
    async def to_dict(user: User) -> dict[str, Any]:
        return {
            "id": user.id,
            "email": user.email,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
        }
