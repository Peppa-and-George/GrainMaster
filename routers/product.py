from typing import Literal, Optional, Union, List

from fastapi import Query, HTTPException, status, Body, Form, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from models.base import ProductSchema, ProductBannerSchema, ProductDetailSchema
from schema.common import page_with_order, transform_schema
from schema.database import SessionLocal
from dependency.image import save_image, delete_image, save_upload_image
from schema.tables import Product, ProductBanner, ProductDetail
from schema.tables import AppletsOrder, AppletsOrderDetail

product_router = APIRouter()


@product_router.get("/get_applet_products_by_id", summary="获取小程序商品信息")
async def get_applets_product_by_id_api(
    product_id: int = Query(..., description="商品id"),
):
    """
    # 获取小程序商品信息
    ## params
    - **product_id**: 商品id

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


@product_router.get("/get_product_banner", summary="获取指定商品的banner")
async def get_product_banner_api(
    product_id: int = Query(..., description="商品id"),
):
    """
    # 获取指定商品的banner
    ## params
    - **product_id**: 商品id
    """
    with SessionLocal() as db:
        banners = db.query(ProductBanner).filter_by(product_id=product_id).all()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "code": 0,
                "message": "查询成功",
                "data": transform_schema(ProductBannerSchema, banners),
            },
        )


@product_router.get("/get_product_detail", summary="获取指定商品的详情")
async def get_product_detail_api(
    product_id: int = Query(..., description="商品id"),
):
    """
    # 获取指定商品的详情
    ## params
    - **product_id**: 商品id
    """
    with SessionLocal() as db:
        details = db.query(ProductDetail).filter_by(product_id=product_id).all()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "code": 0,
                "message": "查询成功",
                "data": transform_schema(ProductDetailSchema, details),
            },
        )


@product_router.get("/get_products", summary="获取商品列表")
async def get_products_api(
    product: Union[str, int] = Query(None, description="商品名称或id"),
    product_field_type: Literal["name", "id"] = Query("name", description="商品字段类型"),
    price_min: Optional[float] = Query(None, description="最小价格"),
    price_max: Optional[float] = Query(None, description="最大价格"),
    synchronize: Optional[bool] = Query(None, description="是否同步"),
    remain: Optional[bool] = Query(None, description="是否有库存"),
    page: int = Query(1, description="页码"),
    per_page: int = Query(10, description="每页数量"),
    order: Literal["asc", "desc"] = Query("asc", description="排序方式"),
    order_field: str = Query("id", description="排序字段"),
):
    """
    # 获取商品列表
    ## params
    - **product**: 商品名称或id, 可选, int or str
    - **product_field_type**: 商品字段类型, 可选, 默认name, 可选值: name, id
    - **price_min**: 最小价格, 可选, 浮点数
    - **price_max**: 最大价格, 可选, 浮点数
    - **synchronize**: 是否同步, 可选, 布尔值
    - **remain**: 是否有库存, 可选, 布尔值
    - **page**: 页码, 可选, 默认1
    - **per_page**: 每页数量, 可选, 默认10
    - **order**: 排序方式, 可选, 默认asc
    - **order_field**: 排序字段, 可选, 默认id
    """
    with SessionLocal() as db:
        query = (
            db.query(Product)
            .outerjoin(ProductBanner, Product.id == ProductBanner.product_id)
            .outerjoin(ProductDetail, Product.id == ProductDetail.product_id)
        )
        if product:
            if product_field_type == "name":
                query = query.filter(Product.name.like(f"%{product}%"))
            else:
                query = query.filter(Product.id == product)
        if price_min:
            query = query.filter(Product.price >= price_min)
        if price_max:
            query = query.filter(Product.price <= price_max)
        if synchronize is not None:
            query = query.filter(Product.synchronize == synchronize)
        if remain is not None:
            if remain:
                query = query.filter(Product.amount > 0)
            else:
                query = query.filter(Product.amount <= 0)
        response = page_with_order(
            schema=ProductSchema,
            query=query,
            page=page,
            page_size=per_page,
            order=order,
            order_field=order_field,
            distinct_field=Product.id,
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"code": 0, "message": "获取成功", "data": response},
        )


@product_router.post(
    "/add_product",
    summary="添加商品",
)
async def add_product_api(
    product_name: str = Body(..., description="商品名称"),
    introduction: Optional[str] = Body(None, description="商品介绍"),
    price: float = Body(..., description="商品价格"),
    unit: float = Body(..., description="商品规格"),
    icon: str = Body(..., description="商品图片"),
    synchronize: Optional[bool] = Body(False, description="是否同步"),
    amount: Optional[int] = Body(0, description="数量", examples=[100, 200]),
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
    - **amount**: 库存数量，整型，可选
    """
    try:
        icon = save_image(icon) if icon else None

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
            db.flush()
            db.refresh(product)
            db.commit()
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "code": 0,
                    "message": "添加成功",
                    "data": transform_schema(ProductSchema, product),
                },
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@product_router.post("add_product_form", summary="添加商品（参数为表单）")
async def add_product_form_api(
    product_name: str = Form(..., description="商品名称"),
    introduction: Optional[str] = Form(None, description="商品介绍"),
    price: float = Form(..., description="商品价格"),
    unit: float = Form(..., description="商品规格"),
    icon: UploadFile = File(..., description="商品图片"),
    synchronize: bool = Form(False, description="是否同步"),
    amount: Optional[int] = Form(0, description="数量", examples=[100, 200]),
):
    """
    # 添加商品, 表单参数
    ## params
    - **productN_name**: 商品名称，字符串， 必填
    - **introduction**: 商品介绍，字符串，可选
    - **price**: 价格，浮点数，必填
    - **unit**: 规格，浮点数，必填
    - **icon**: 图片二进制数据, 必填
    - **synchronize**: 是否同步，布尔值，默认值false可选
    - **amount**: 库存数量，整型，可选, 默认值0
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
            db.flush()
            db.refresh(product)
            db.commit()
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "code": 0,
                    "message": "添加成功",
                    "data": transform_schema(ProductSchema, product),
                },
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@product_router.post("/upload_banner", summary="上传商品banner")
async def upload_banner_api(
    product_id: int = Form(..., description="商品id"),
    banners: List[UploadFile] = File(..., description="banner封面"),
):
    """
    # 上传商品banner
    ## params
    - **product_id**: 商品id, 必填
    - **banners**: banner封面, 必填, List[File]
    """
    try:
        with SessionLocal() as db:
            product = db.query(Product).filter_by(id=product_id).first()
            if product is None:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={
                        "code": 1,
                        "message": "上传失败, 该商品不存在",
                    },
                )
            for index, banner in enumerate(banners):
                icon_filename = save_upload_image(banner)
                banner_file = ProductBanner(filename=icon_filename, index=index + 1)
                product.product_banners.append(banner_file)
            db.flush()
            db.commit()
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "code": 0,
                    "message": "上传成功",
                    "data": transform_schema(ProductSchema, product),
                },
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@product_router.post("/upload_detail", summary="上传商品详情")
async def upload_detail_api(
    product_id: int = Form(..., description="商品id"),
    details: List[UploadFile] = File(..., description="商品详情"),
):
    """
    # 上传商品详情
    ## params
    - **product_id**: 商品id, 必填
    - **details**: 商品详情, 必填, List[File]
    """
    try:
        with SessionLocal() as db:
            product = db.query(Product).filter_by(id=product_id).first()
            if product is None:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={
                        "code": 1,
                        "message": "上传失败, 该商品不存在",
                    },
                )
            for index, detail in enumerate(details):
                icon_filename = save_upload_image(detail)
                detail_file = ProductDetail(filename=icon_filename, index=index + 1)
                product.product_details.append(detail_file)
            db.flush()
            db.commit()
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "code": 0,
                    "message": "上传成功",
                    "data": transform_schema(ProductSchema, product),
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
            if icon:
                delete_image(icon)
            for banner in product.product_banners:
                db.delete(banner)
            for detail in product.product_details:
                db.delete(detail)
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


@product_router.delete("/delete_banner", summary="删除商品banner")
async def delete_banner_api(
    banner_id: int = Query(..., description="banner id", example=1)
):
    """
    # 删除商品banner
    - **banner_id**: banner ID, 整型，必填
    """
    try:
        with SessionLocal() as db:
            banner = db.query(ProductBanner).filter_by(id=banner_id).first()
            if banner is None:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={
                        "code": 1,
                        "message": "删除失败, 该banner不存在",
                    },
                )
            db.delete(banner)
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


@product_router.delete("/delete_detail", summary="删除商品详情")
async def delete_detail_api(
    detail_id: int = Query(..., description="详情 id", example=1)
):
    """
    # 删除商品详情
    - **detail_id**: 详情 ID, 整型，必填
    """
    try:
        with SessionLocal() as db:
            detail = db.query(ProductDetail).filter_by(id=detail_id).first()
            if detail is None:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={
                        "code": 1,
                        "message": "删除失败, 该详情不存在",
                    },
                )
            db.delete(detail)
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


@product_router.delete("/delete_all_banners", summary="删除商品所有banner")
async def delete_all_banners_api(
    product_id: int = Query(..., description="商品id", example=1)
):
    """
    # 删除商品所有banner
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
            for banner in product.product_banners:
                db.delete(banner)
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


@product_router.delete("/delete_all_details", summary="删除商品所有详情")
async def delete_all_details_api(
    product_id: int = Query(..., description="商品id", example=1)
):
    """
    # 删除商品所有详情
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
            for detail in product.product_details:
                db.delete(detail)
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
