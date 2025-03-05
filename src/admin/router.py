import resend
from fastapi import APIRouter, Depends
from pydantic import EmailStr
from sqlalchemy import select, func, delete, update


from src.admin.schemas import UserViewForAdmin, UserViewForAdminDetail, UserViewForAdminBlockList
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
        query = select(User).where(User.is_superuser==False).order_by(User.is_blocked, User.registered_at)
        mas_us = await session.execute(query)
        mas = mas_us.unique().scalars().all()
        lmas = [UserViewForAdmin.model_validate(c) for c in mas]
        if not lmas:
            return {"status": 404, "message": "Not a single User was found."}
        else:
            return {"status": 200, "Products": lmas}

@router.get("/get_blocked_user_list/", summary="Get all block users")
async def get_blocked_user_list(user: User = Depends(adm_user)):
    async with async_session() as session:
        query = select(User).filter_by(is_superuser=False, is_blocked=True).order_by(User.registered_at)
        mas_us = await session.execute(query)
        mas = mas_us.unique().scalars().all()
        lmas = [UserViewForAdminBlockList.model_validate(c) for c in mas]
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

@router.post("/block_user/{user_email}/{status_blocked}/", summary="Block/Unblock suspicious user", description="")
async def block_user(user_email: EmailStr, status_blocked: bool,  user: User = Depends(adm_user)):
    """
    True - Block a user\n
    False - Unblock a user
    """
    async with async_session() as session:
        query = select(User).filter_by(email=user_email, is_superuser=False)
        bl_q = await session.execute(query)
        bl_r = bl_q.unique().scalars().all()
        try:
            if bl_r:
                stmt = (
                    update(User)
                    .values(is_blocked=status_blocked)
                    .filter_by(email=user_email)
                )
                await session.execute(stmt)
                await session.commit()

                if status_blocked:
                    # noinspection PyTypeChecker
                    params: resend.Emails.SendParams = {
                        "from": "AccountingDA@petproject.website",
                        "to": user_email,
                        "subject": "Your account is blocked",
                        "html": f"<h2>Your account has been blocked by Administrator {user.username} {user.surname}</h2>",
                    }
                    email: resend.Email = resend.Emails.send(params)
                    print(f"The user with email address {user_email} is blocked")
                    return {
                        "status": 200,
                        "message": f"The user with email address {user_email} is blocked",
                        }

                else:
                    # noinspection PyTypeChecker
                    params: resend.Emails.SendParams = {
                        "from": "AccountingDA@petproject.website",
                        "to": user_email,
                        "subject": "Your account is unblocked",
                        "html": f"<h2>Your account has been unblocked by Administrator {user.username} {user.surname}</h2>",
                    }
                    email: resend.Email = resend.Emails.send(params)
                    print(f"The user with email address {user_email} is unblocked")
                    return {
                        "status": 200,
                        "message": f"The user with email address {user_email} is unblocked",
                    }

            return {"message": f"User with email address {user_email} not found"}
        except:
            return {
                "Error": "Unknown error"
            }

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