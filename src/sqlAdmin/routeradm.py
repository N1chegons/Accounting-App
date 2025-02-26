from fastapi import APIRouter

from src.auth.router import fastapi_users
from src.auth.schemas import UserRead, UserCreate

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)

adm_user = fastapi_users.current_user(superuser=True)
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
)