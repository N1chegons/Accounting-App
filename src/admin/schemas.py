import datetime

from pydantic import BaseModel, EmailStr, ConfigDict

from src.product.schemas import ProductV


class UserViewForAdmin(BaseModel):
    id: int
    username: str
    surname: str
    email: EmailStr
    registered_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)

class UserViewForAdminBlockList(UserViewForAdmin):
    is_blocked: bool

    model_config = ConfigDict(from_attributes=True)

class UserViewForAdminDetail(UserViewForAdmin):
    products: list["ProductV"]

    model_config = ConfigDict(from_attributes=True)




