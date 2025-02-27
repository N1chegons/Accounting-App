import datetime

from pydantic import BaseModel, Field, ConfigDict

from src.entites.models import Status


class ProductCreate(BaseModel):
    name: str = Field(max_length=40)
    price: int = Field(ge=1)
    user_id: int = Field(ge=1)

class ProductV(BaseModel):
    id: int
    name: str
    price: int
    status: Status
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)

class ProductVU(ProductV):
    user_id: int

    model_config = ConfigDict(from_attributes=True)
