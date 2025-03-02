from fastapi import APIRouter
from fastapi.params import Depends, Query
from sqlalchemy import select, update

from src.auth.router import cur_user
from src.db import async_session
from src.entites.models import ProductTable, Status, User
from src.product.schemas import ProductCreate, ProductVU

router = APIRouter(
    prefix="/product",
    tags=["Products"]
)

@router.get("/get_all_products/", summary="Get a list of products")
async def get_product_list(user: User = Depends(cur_user)):
    async with async_session() as session:
        query = select(ProductTable).order_by(ProductTable.created_at)
        result = await session.execute(query)
        ans = result.unique().scalars().all()
        ans_pr = [ProductVU.model_validate(p) for p in ans]
        if not ans_pr:
            return{"message": "There is not a single product"}
        else:
            return {"status": 200, "Products": ans_pr}

@router.get("/get_your_products/", summary="Get a list of your products")
async def get_local_product_list(user: User = Depends(cur_user)):
    async with async_session() as session:
        query = select(ProductTable).filter_by(user_id=user.id).order_by(ProductTable.price)
        result = await session.execute(query)
        ans = result.unique().scalars().all()
        ans_pr = [ProductVU.model_validate(p) for p in ans]
        if not ans_pr:
            return{"message": "There is not a single product"}
        else:
            return {"status": 200, "Your products": ans_pr}

@router.get("/get_status_product/{status}/", summary="Get a list of products with status(sold/unsold)")
async def get_product_list_with_status(status: Status, user: User = Depends(cur_user)):
    async with async_session() as session:
        query = select(ProductTable).filter_by(status=status)
        result = await session.execute(query)
        ans = result.scalars().all()
        ans_pr = [ProductVU.model_validate(p) for p in ans]
        if not ans_pr:
            return{"message": "There is not a single product"}
        else:
            return {"status": 200, "Products": ans_pr}

@router.post("/create_product/", summary="Create one product")
async def create_product(pr: ProductCreate = Depends(), user: User = Depends(cur_user)):
    async with async_session() as session:
        pr_d = pr.model_dump()
        pr_s = ProductTable(**pr_d)
        if pr_s.user_id == user.id:
            session.add(pr_s)
            await session.flush()
            await session.commit()
            return {"status": 201, "message": "Product created", "creator": f"{user.username} {user.surname}"}
        else:
            return {"status": 422, "message": f"Enter your ID, your ID does not match the one you entered({pr_s.user_id})."}

@router.put("/edit_product_info/{product_id}/", summary="Edit product")
async def edit_product(product_id: int ,name: str = Query(max_length=40), price: int = Query(ge=1), user: User = Depends(cur_user)):
    async with async_session() as session:
        query = select(ProductTable).filter_by(id=product_id, user_id=user.id)
        res = await session.execute(query)
        pr_s = res.scalars().all()
        # noinspection PyBroadException
        try:
            if pr_s:
                stmt = (
                    update(ProductTable)
                    .values(name=name, price=price)
                    .filter_by(id=product_id)
                )
                await session.execute(stmt)
                await session.commit()

                return {
                    "status": 200,
                    "message": "Product info edited"
                }
            else:
                return {"status": 404, "message": f"Product with {product_id} not found"}
        except:
            return {
                "status": 422,
                "Error": "Check the value of the fields, and try again"
            }

@router.put("/sale_product/{product_id}/", summary="Product Sale")
async def product_sale(product_id: int, user: User = Depends(cur_user)):
    async with async_session() as session:
        query = select(ProductTable).filter_by(id=product_id, user_id=user.id)
        res = await session.execute(query)
        pr_s = res.scalars().all()
        # noinspection PyBroadException
        try:
            if pr_s:
                stmt = (
                    update(ProductTable)
                    .values(status=Status.sold)
                    .filter_by(id=product_id)
                )
                await session.execute(stmt)
                await session.commit()

                return {
                    "status": 200,
                    "message": "Product Sale",
                    "Seller": f"{user.username} {user.surname}"
                }
            else:
                return {"status": 404, "message": f"Product with {product_id} not found", "seller": f"{user.username} {user.surname}"}
        except:
            return {
                "status": 422,
                "Error": "There is no such product"
            }

@router.delete("/delete_product/{product_id}/", summary="Delete one Product")
async def delete_product(product_id: int, user_id: int, user: User = Depends(cur_user)):
    async with async_session() as session:
        # noinspection PyBroadException
        try:
            if user_id == user.id:
                del_prod = await session.get(ProductTable, product_id)
                await session.delete(del_prod)
                await session.commit()
                return {
                    "status": 200,
                    "message": f"Product with {product_id} deleted",
                    "Deleted it": f"{user.username} {user.surname}",
                        }
            else:
                return{"status": 404, "message": "Please check column <user_id>"}
        except:
            print(del_prod)
            return {
                "status": 404,
                "message": f"Product with {product_id} was not found"
            }

