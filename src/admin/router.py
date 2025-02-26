from fastapi import APIRouter, Depends
from sqlalchemy import select, func, delete

from src.auth.router import fastapi_users
from src.auth.schemas import UserRead, UserCreate
from src.db import async_session
from src.entites.models import User, ProductTable

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

@router.delete("/clear_product_list/", summary="Clear all product DB")
async def clear_product_list(user: User = Depends(adm_user)):
    async with async_session() as session:
        count = await session.execute(select(func.count()).select_from(ProductTable))
        count_cl = count.scalar()
        # noinspection PyBroadException
        try:
            if count_cl > 0:
                stmt = delete(ProductTable)
                await session.execute(stmt)
                await session.commit()
                return {"status": 200, "message": "Products list clear", "Deleted all products":f"Admin {user.username}"}
            else:
                return {"status": 404, "message": "The list of products is empty"}
        except:
            return {"status": 404, "message": "Something went wrong..."}



router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/register_new_user"
)