import datetime

from fastapi_users import schemas
from pydantic import EmailStr

from src.product.schemas import ProductV


class UserRead(schemas.BaseUser[int]):
    id: int
    username: str
    surname: str
    email: EmailStr
    password: str
    registered_at: datetime.datetime
    is_superuser: bool
    products: list["ProductV"]

class UserCreate(schemas.BaseUserCreate):
    username: str
    surname: str
    password: str
    email: EmailStr
