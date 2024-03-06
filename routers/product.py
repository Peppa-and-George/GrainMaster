from typing import Literal, Optional

from fastapi import Query, HTTPException, status, Body, Form, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from models.base import ProductSchema
from schema.common import page_with_order
from schema.product import get_products, get_products_by_name
from schema.database import SessionLocal

from dependency.image import save_image, delete_image, save_upload_image
from schema.tables import Product
from schema.tables import AppletsOrder, AppletsOrderDetail

product_router = APIRouter()


@product_router.get("/get_products", summary="批量获取商品信息")
async def get_products_api(
    order_field: str = Query("id", description="排序字段"),
    order: Literal["desc", "asc"] = Query("asc", description="排序方式"),
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
):
    """
    # 批量获取商品信息
    ## params
    - **page**: 页码, 从1开始, 可选
    - **page_size**: 分页大小，默认20，范围1-100, 可选
    - **order_field**: 排序字段, 默认为"id", 可选
    - **order**: 排序方式, asc: 升序, desc: 降序, 默认升序， 可选
    """
    try:
        query = get_products()
        response = page_with_order(
            schema=ProductSchema,
            query=query,
            page=page,
            page_size=page_size,
            order_field=order_field,
            order=order,
        )
        response.update({"code": 0, "message": "查询成功"})
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@product_router.get("/get_products_by_name", summary="根据商品名称获取商品信息")
async def get_product_by_name_api(
    name: str = Query(..., description="商品名称", example="test"),
    fuzzy: bool = Query(False, description="是否模糊查询"),
    order_field: str = Query("id", description="排序字段"),
    order: Literal["desc", "asc"] = Query("asc", description="排序方式"),
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
):
    """
    # 根据商品名称获取商品信息
    ## params
    - **name**: 商品名称
    - **fuzzy**: 是否模糊查询, 默认False, 可选
    - **page**: 页码, 从1开始, 可选
    - **page_size**: 分页大小，默认20，范围1-100, 可选
    - **order_field**: 排序字段, 默认为"id", 可选
    - **order**: 排序方式, asc: 升序, desc: 降序, 默认升序， 可选
    - **page_size**: 分页大小，默认10，范围1-100, 可选
    """
    try:
        query = get_products_by_name(
            name=name,
            fuzzy=fuzzy,
        )
        response = page_with_order(
            schema=ProductSchema,
            query=query,
            page=page,
            page_size=page_size,
            order_field=order_field,
            order=order,
        )
        response.update({"code": 0, "message": "查询成功"})
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@product_router.get("/get_applets_products_by_id", summary="获取小程序商品信息")
async def get_applets_products_by_id_api(
    product_id: int = Query(..., description="商品id"),
):
    sales_volume = 0
    """
    # 获取小程序商品信息
    ## params
    - **productName**: 商品名称
    
    ## response
    - **id**: 商品ID
    - **name**: 商品名称
    - **introduction**: 商品介绍
    - **price**: 价格
    - **unit**: 规格
    - **amount**: 库存
    - **icon**: 商品图片名称
    - **sales_volume**: 销量
    """
    with SessionLocal() as db:
        product = (
            db.query(Product)
            .filter(
                Product.id == product_id,
                Product.synchronize == True,
            )
            .first()
        )
        if not product:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "code": 1,
                    "message": "查询失败, 该商品不存在",
                },
            )

        # 统计销量
        sales_volume = 0
        order_details = (
            db.query(AppletsOrderDetail)
            .join(AppletsOrder, AppletsOrder.id == AppletsOrderDetail.order_id)
            .join(Product, Product.id == AppletsOrderDetail.product_id)
            .filter(
                AppletsOrderDetail.product_id == product_id,
                AppletsOrder.status != "待支付",
            )
        )
        for item in order_details:
            sales_volume += item.quantity
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "code": 0,
                "message": "查询成功",
                "data": {
                    "id": product.id,
                    "name": product.name,
                    "introduction": product.introduction,
                    "price": product.price,
                    "unit": product.unit,
                    "icon": product.icon,
                    "amount": product.amount,
                    "sales_volume": sales_volume,
                },
            },
        )


@product_router.get("/get_product_by_id", summary="根据id获取商品信息")
async def get_product_api(
    product_id: int = Query(..., description="商品id", alias="productId"),
):
    """
    # 根据id获取商品信息
    ## params
    - **productName**: 商品名称
    - **fuzzy**: 是否模糊查询, 默认False, 可选
    - **page**: 页码, 从1开始, 可选
    - **page_size**: 分页大小，默认20，范围1-100, 可选
    - **order_field**: 排序字段, 默认为"id", 可选
    - **order**: 排序方式, asc: 升序, desc: 降序, 默认升序， 可选
    """
    try:
        product = get_products().filter_by(id=product_id).first()
        if product is None:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "code": 1,
                    "message": "查询失败, 该商品不存在",
                },
            )
        product_data = ProductSchema.model_validate(
            product, from_attributes=True
        ).model_dump()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "code": 0,
                "message": "查询成功",
                "data": [product_data],
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@product_router.post(
    "/add_product",
    summary="添加商品",
)
async def add_product_api(
    product_name: str = Body(..., description="商品名称"),
    introduction: Optional[str] = Body(None, description="商品介绍"),
    price: Optional[float] = Body(None, description="商品价格"),
    unit: Optional[float] = Body(None, description="商品规格"),
    icon: Optional[str] = Body(None, description="商品图片"),
    synchronize: Optional[bool] = Body(False, description="是否同步"),
    amount: Optional[int] = Body(None, description="数量", examples=[100, 200]),
):
    """
    # 添加商品
    ## params
    - **productN_name**: 商品名称，字符串， 必填
    - **introduction**: 商品介绍，字符串，可选
    - **price**: 价格，浮点数，必填
    - **unit**: 规格，浮点数，必填
    - **icon**: base64格式图片，字符串，必填, 示例：data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAY
    - **synchronize**: 是否同步，布尔值，默认值false可选
    - **amount**: 数量，整型，可选
    """
    try:
        icon = save_image(icon) if icon else None

        with SessionLocal() as db:
            product = Product(
                **{
                    "name": product_name,
                    "introduction": introduction,
                    "price": price,
                    "unit": unit,
                    "icon": icon,
                    "synchronize": synchronize,
                    "amount": amount if amount else 0,
                }
            )
            db.add(product)
            db.commit()
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "code": 0,
                    "message": "添加成功",
                },
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@product_router.post("add_product_form", summary="添加商品（参数为表单）")
async def add_product_form_api(
    product_name: str = Form(..., description="商品名称"),
    introduction: Optional[str] = Form(None, description="商品介绍"),
    price: Optional[float] = Form(None, description="商品价格"),
    unit: Optional[float] = Form(None, description="商品规格"),
    icon: Optional[UploadFile] = File(None, description="商品图片"),
    synchronize: Optional[bool] = Form(False, description="是否同步"),
    amount: Optional[int] = Form(0, description="数量", examples=[100, 200]),
):
    """
    # 添加商品, 表单参数
    ## params
    - **productN_name**: 商品名称，字符串， 必填
    - **introduction**: 商品介绍，字符串，可选
    - **price**: 价格，浮点数，必填
    - **unit**: 规格，浮点数，必填
    - **icon**: base64格式图片，字符串，必填, 示例：data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAY
    - **synchronize**: 是否同步，布尔值，默认值false可选
    - **amount**: 数量，整型，可选
    """
    try:
        icon = save_upload_image(icon) if icon else None
        with SessionLocal() as db:
            product = Product(
                name=product_name,
                introduction=introduction,
                price=price,
                unit=unit,
                icon=icon,
                synchronize=synchronize,
                amount=amount,
            )
            db.add(product)
            db.commit()
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "code": 0,
                    "message": "添加成功",
                },
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@product_router.put("/update_product", summary="更新商品")
async def update_product_api(
    product_id: int = Body(..., description="商品id"),
    product_name: Optional[str] = Body(None, description="商品名称"),
    introduction: Optional[str] = Body(None, description="商品介绍"),
    price: Optional[float] = Body(None, description="商品价格"),
    unit: Optional[float] = Body(None, description="商品规格"),
    icon: Optional[str] = Body(None, description="商品图片"),
    synchronize: Optional[bool] = Body(None, description="是否同步"),
):
    """
    # 更新商品
    - **id**: 商品ID, 整型，必填
    - **product_name**: 商品名称，字符串， 可选
    - **introduction**: 商品介绍，字符串，可选
    - **price**: 价格，浮点数，可选
    - **unit**: 规格，浮点数，可选
    - **icon**: base64格式图片，字符串，可选, 示例：data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAY
    - **synchronize**: 是否同步，布尔值，默认值false可选
    """
    try:
        with SessionLocal() as db:
            product = db.query(Product).filter_by(id=product_id).first()
            if product is None:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={
                        "code": 1,
                        "message": "更新失败, 该商品不存在",
                    },
                )
            if product_name is not None:
                product.name = product_name
            if introduction is not None:
                product.introduction = introduction
            if price is not None:
                product.price = price
            if unit is not None:
                product.unit = unit
            if icon is not None:
                delete_image(product.icon)
                product.icon = save_image(icon)
            if synchronize is not None:
                product.synchronize = synchronize
            db.commit()
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "code": 0,
                    "message": "更新成功",
                },
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@product_router.put("/update_product_form", summary="更新商品（参数为表单）")
async def update_product_form_api(
    product_id: int = Form(..., description="商品id"),
    product_name: Optional[str] = Form(None, description="商品名称"),
    introduction: Optional[str] = Form(None, description="商品介绍"),
    price: Optional[float] = Form(None, description="商品价格"),
    unit: Optional[float] = Form(None, description="商品规格"),
    icon: Optional[UploadFile] = File(None, description="商品图片"),
    synchronize: Optional[bool] = Form(None, description="是否同步"),
):
    """
    # 更新商品, 表单参数
    - **id**: 商品ID, 整型，必填
    - **product_name**: 商品名称，字符串， 可选
    - **introduction**: 商品介绍，字符串，可选
    - **price**: 价格，浮点数，可选
    - **unit**: 规格，浮点数，可选
    - **icon**: 图片二进制数据
    - **synchronize**: 是否同步，布尔值，默认值false可选
    """
    try:
        with SessionLocal() as db:
            product = db.query(Product).filter_by(id=product_id).first()
            if product is None:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={
                        "code": 1,
                        "message": "更新失败, 该商品不存在",
                    },
                )
            if product_name is not None:
                product.name = product_name
            if introduction is not None:
                product.introduction = introduction
            if price is not None:
                product.price = price
            if unit is not None:
                product.unit = unit
            if icon is not None:
                delete_image(product.icon)
                product.icon = save_upload_image(icon)
            if synchronize is not None:
                product.synchronize = synchronize
            db.commit()
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "code": 0,
                    "message": "更新成功",
                },
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@product_router.delete("/delete_product", summary="删除商品")
async def delete_product_api(
    product_id: int = Query(..., description="商品id", example=1)
):
    """
    # 删除商品
    - **product_id**: 商品ID, 整型，必填
    """
    try:
        with SessionLocal() as db:
            product = db.query(Product).filter_by(id=product_id).first()
            if product is None:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={
                        "code": 1,
                        "message": "删除失败, 该商品不存在",
                    },
                )
            icon = product.icon
            delete_image(icon)
            db.delete(product)
            db.commit()
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "code": 0,
                    "message": "删除成功",
                },
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
