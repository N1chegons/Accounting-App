from sqladmin import ModelView
from src.entites.models import ProductTable, User


class ProductTableAdm(ModelView, model=ProductTable):
    name = "Product"
    name_plural = "Products"

    column_list=[ProductTable.id, ProductTable.name]

class UserTableAdm(ModelView, model=User):
    name = "User"
    name_plural = "Users"

    column_list=[User.id, User.username, User.surname]
