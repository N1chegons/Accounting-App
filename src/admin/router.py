from fastapi import APIRouter, Depends
from sqlalchemy import select

from src.auth.router import fastapi_users
from src.auth.schemas import UserRead, UserCreate
from src.db import async_session
from src.entites.models import User

router = APIRouter(
    prefix="/admins",
    tags=["Admin"],
)

adm_user = fastapi_users.current_user(superuser=True)

@router.get("/get_user_list/")
async def get_user_list(user: User = Depends(adm_user)):
    async with async_session() as session:
        query = select(User).where(User.is_superuser==False).order_by(User.registered_at)
        mas_us = await session.execute(query)
        mas = mas_us.scalars().all()
        return {"users": mas}

router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
)