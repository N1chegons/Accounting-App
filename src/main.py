from fastapi import FastAPI
from sqladmin import Admin

from src.product.router import router as product_router
from src.auth.router import router as user_router
from src.db import async_engine
from src.sqlAdmin.connect import ProductTableAdm, UserTableAdm

app = FastAPI(
    title="Accounting",
    description="""
                This is a personal accounting app.
        
                Create your own products and see the entries.
                """
)
admin = Admin(app, async_engine)

# APIRouters connect
app.include_router(user_router)
app.include_router(product_router)

# SQLAdmin views
admin.add_view(ProductTableAdm)
admin.add_view(UserTableAdm)
