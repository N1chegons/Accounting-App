from fastapi import Depends, APIRouter
from fastapi_users import FastAPIUsers
from pydantic import EmailStr
from sqlalchemy import select, update

from src.auth.config import auth_backend
from src.auth.manager import get_user_manager
from src.auth.schemas import UserRead, UserCreate
from src.db import async_session
from src.entites.models import User
from src.product.schemas import ProductV

router = APIRouter(
    prefix="/user",
    tags=["User"],
)

# conf fastapi_users
fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)


cur_user = fastapi_users.current_user()
@router.get("/account", summary="Account View")
def protected_route(user: User = Depends(cur_user)):
    return {"status": 200,
            "Id": user.id,
            "Username": user.username,
            "Surname": user.surname,
            "Email": user.email,
            "Status": "Admin",
            "Your product": [ProductV.model_validate(p) for p in user.products],
            }

@router.put("/change_data/", summary="Change user data")
async def change_data_for_user(new_username: str, new_surname: str, new_email: EmailStr,user: User = Depends(cur_user)):
    async with async_session() as session:
        query = select(User).where(User.id==user.id)
        result = await session.execute(query)
        res = result.scalars().all()
        try:
            if res:
                stmt = (
                    update(User)
                    .values(username=new_username, surname=new_surname, email=new_email)
                    .filter_by(id=user.id)
                )
                await session.execute(stmt)
                await session.commit()

                return {
                    "status": 200,
                    "message": "User data edited"
                }
            else:
                return {"status": 404, "message": f"User undefiled"}
        except:
            return {
                "status": 422,
                "Error": "Check the value of the fields, and try again"
            }

#auth
router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
)
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
)