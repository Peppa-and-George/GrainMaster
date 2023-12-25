from typing import List

from fastapi import Depends, Query, HTTPException, status, Body
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter

from models.common import ResStatus
from models.product_model import (
    QueryProductsResponseModel,
    QueryProductsModel,
    ProductSchema,
    AddProductModel,
    AddProductResponseModel,
    AddProductsResponseModel,
    UpdateProductModel,
)
from schema.product import (
    query_products,
    query_product_by_id,
    add_products,
    Product,
    add_product,
    update_product,
    delete_product_by_id,
)
from dependency.upload_image import save_image, save_images, update_image, delete_image

product_router = APIRouter(prefix="/product", tags=["产品管理"])


@product_router.get(
    "/get_products", description="获取所有商品信息", response_model=QueryProductsResponseModel
)
async def get_products_api(
    query_model: QueryProductsModel = Depends(),
):
    """
    获取所有商品信息
    :param query_model: 查询参数
    """
    try:
        res = query_products(query_model)
        products_data = QueryProductsResponseModel.model_validate(
            res, from_attributes=True
        )
        products_data.message = "查询成功"
        return JSONResponse(
            status_code=status.HTTP_200_OK, content=products_data.model_dump()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@product_router.get(
    "/get_product_by_id", description="根据id获取商品信息", response_model=ResStatus
)
async def get_product_api(
    product_id: int = Query(..., description="商品id", alias="productId"),
):
    """
    根据id获取商品信息
    :param product_id: 商品id
    """
    try:
        res = query_product_by_id(product_id)
        if res is None:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=ResStatus(
                    **{"code": 1, "message": "查询失败, 该商品不存在"}
                ).model_dump(),
            )
        product_data = ProductSchema.model_validate(res, from_attributes=True)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=ResStatus(
                **{"code": 0, "message": "查询成功", "data": product_data}
            ).model_dump(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@product_router.post(
    "/add_product",
    description="添加商品",
    response_model=AddProductResponseModel,
    dependencies=[Depends(save_image)],
)
async def add_product_api(product: AddProductModel = Depends(save_image)):
    """
    添加商品
    :param product: 商品信息
    """
    try:
        add_product(Product(**product.model_dump()))
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=AddProductResponseModel(
                **{"code": 0, "message": "添加成功"}
            ).model_dump(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@product_router.post(
    "/add_products", description="批量添加商品", response_model=AddProductsResponseModel
)
async def add_products_api(
    products: List[AddProductModel] = Depends(save_images),
):
    """
    批量添加商品
    :param products: 商品信息
    """
    try:
        add_products([Product(**product.model_dump()) for product in products])
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=AddProductsResponseModel(
                **{"code": 0, "message": "添加成功"}
            ).model_dump(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@product_router.put("/update_product", description="更新商品")
async def update_product_api(
    query: UpdateProductModel = Depends(update_image),
):
    """
    更新商品
    :param query: 商品信息
    """
    try:
        updated_row = update_product(
            product_id=query.product_id,
            product=Product(**query.product.model_dump()),
        )
        if updated_row == 0:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=AddProductResponseModel(
                    **{"code": 1, "message": "更新失败, 该商品不存在"}
                ).model_dump(),
            )
        else:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=AddProductResponseModel(
                    **{"code": 0, "message": "更新成功"}
                ).model_dump(),
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@product_router.delete("/delete_product", description="删除商品")
async def delete_product_api(
    product_id: int = Depends(delete_image),
):
    """
    删除商品
    :param product_id: 商品id
    """
    try:
        deleted_row = delete_product_by_id(product_id)
        if deleted_row == 0:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=AddProductResponseModel(
                    **{"code": 1, "message": "删除失败, 该商品不存在"}
                ).model_dump(),
            )
        else:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=AddProductResponseModel(
                    **{"code": 0, "message": "删除成功"}
                ).model_dump(),
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
