import datetime
import enum

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from pydantic import EmailStr
from pygments.lexer import default
from sqlalchemy import text, ForeignKey
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.testing.schema import mapped_column

from src.db import Base as BaseMain

class Status(enum.Enum):
    sold = "sold"
    unsold = "unsold"

class User(SQLAlchemyBaseUserTable[int], BaseMain):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(nullable=False)
    surname: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[EmailStr]
    hashed_password: Mapped[str]
    registered_at: Mapped[datetime.datetime] = mapped_column(
        server_default=text(
            "TIMEZONE('utc', now())")
    )
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_verified: Mapped[bool] = mapped_column(default=True, nullable=False)
    is_blocked: Mapped[bool] = mapped_column(default=False, nullable=False)

    products: Mapped[list["ProductTable"]] = relationship(
        back_populates="creator",
        lazy="joined",
    )


class ProductTable(BaseMain):
    __tablename__ = "products"

    id: Mapped[int]=mapped_column(primary_key=True)
    name: Mapped[str]
    price: Mapped[int]
    status: Mapped[Status]=mapped_column(default=Status.unsold)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete='CASCADE'))
    created_at: Mapped[datetime.datetime] = mapped_column(
        server_default=text(
        "TIMEZONE('utc', now())")
    )

    creator: Mapped["User"] = relationship(
        back_populates="products",
    )