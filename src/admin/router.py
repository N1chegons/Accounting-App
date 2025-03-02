import resend
from fastapi import APIRouter, Depends
from sqlalchemy import select, func, delete

from src.admin.schemas import UserViewForAdmin, UserViewForAdminDetail
from src.auth.router import fastapi_users
from src.auth.schemas import UserRead, UserCreate
from src.config import settings
from src.db import async_session
from src.entites.models import User, ProductTable

resend.api_key=settings.RESEND_API_KEY

router = APIRouter(
    prefix="/admins",
    tags=["Admin"],
)

adm_user = fastapi_users.current_user(superuser=True)

@router.get("/get_user_list/", summary="Get all users")
async def get_user_list(user: User = Depends(adm_user)):
    async with async_session() as session:
        query = select(User).where(User.is_superuser==False).order_by(User.registered_at)
        mas_us = await session.execute(query)
        mas = mas_us.unique().scalars().all()
        lmas = [UserViewForAdmin.model_validate(c) for c in mas]
        if not lmas:
            return {"status": 404, "message": "Not a single User was found."}
        else:
            return {"status": 200, "Products": lmas}

@router.get("/get_user_detail/{user_id}/", summary="Get concrete user")
async def get_user_detail(user_id: int, user: User = Depends(adm_user)):
    async with async_session() as session:
        query = select(User).filter_by(id=user_id, is_superuser=False)
        us_det = await session.execute(query)
        us_detl = us_det.unique().scalars().all()
        us_details = [UserViewForAdminDetail.model_validate(c) for c in us_detl]
        if not us_details:
            return {"status": 404, "message": f"Not a single User was found with id <<{user_id}>>."}
        else:
            return {"status": 200, "Products": us_details}

@router.post("/block_user/{user_id}/", summary="Block suspicious user")
async def block_user(user_id: int, user: User = Depends(adm_user)):
    async with async_session() as session:
        # noinspection PyTypeChecker
        params: resend.Emails.SendParams = {
            "from": "AccountingDA@petproject.website",
            "to": user.email,
            "subject": "Hello World",
            "html": f"<h1>Token for resent password:</h1>",
        }
        email: resend.Email = resend.Emails.send(params)

        print(f"")
        return email

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

#FA-Users
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/register_new_user"
)