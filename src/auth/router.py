from fastapi import Depends, APIRouter
from fastapi_users import FastAPIUsers
from pydantic import EmailStr
from sqlalchemy import select, update

from src.auth.config import auth_backend
from src.auth.manager import get_user_manager
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
    status_user = ""
    if not user.is_blocked:
        if user.is_superuser:
            status_user = "Admin"
        else:
            status_user = "User"
        return {"status": 200,
                "Id": user.id,
                "Username": user.username,
                "Surname": user.surname,
                "Email": user.email,
                "Status": status_user,
                "Your product": [ProductV.model_validate(p) for p in user.products],
                }
    else:
        return {
                    "status": 423,
                    "message": "Your account is blocked :("
                }

@router.put("/change_data/", summary="Change user data")
async def change_data_for_user(new_username: str, new_surname: str, new_email: EmailStr,user: User = Depends(cur_user)):
    async with async_session() as session:
        query = select(User).filter_by(id=user.id, is_blocked=False)
        result = await session.execute(query)
        res = result.unique().scalars().all()
        # noinspection PyBroadException
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
            if user.is_blocked:
                return {
                    "status": 423,
                    "message": "Your account is blocked :("
                }
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
    fastapi_users.get_reset_password_router(),
    prefix="/reset_password",
)