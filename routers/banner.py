from typing import Optional, Literal

from fastapi.routing import APIRouter
from fastapi import Query, status, Form, UploadFile, File
from fastapi.responses import JSONResponse

from models.base import BannerSchema
from schema.tables import Banner
from schema.database import SessionLocal
from dependency.file import save_upload_file, delete_file
from dependency.image import save_upload_image, delete_image
from schema.common import query_with_page_and_order, transform_schema

banner_router = APIRouter()


@banner_router.get("/get_banner", summary="获取banner列表")
async def get_banner(
    name: Optional[str] = Query(None, description="banner标题"),
    sync_status: Optional[bool] = Query(None, description="同步状态"),
    fuzzy: bool = Query(False, description="模糊查询"),
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    order: Literal["asc", "desc"] = Query("asc", description="排序"),
    order_field: str = Query("id", description="排序字段"),
):
    """
    # 获取banner信息
    ## params
    - **name**: banner标题, 可选
    - **sync_status**: 同步状态, 可选
    - **fuzzy**: 模糊查询, 可选, 默认False
    - **page**: 页码, 从1开始, 可选, 默认1
    - **page_size**: 分页大小，默认10，范围1-100, 可选, 默认10
    - **order**: 排序方式, 可选, 默认asc
    - **order_field**: 排序字段, 可选, 默认id
    """
    with SessionLocal() as db:
        query = db.query(Banner)
        if name:
            if fuzzy:
                query = query.filter(Banner.name.like(f"%{name}%"))
            else:
                query = query.filter(Banner.name == name)
        if sync_status is not None:
            query = query.filter(Banner.synchronize == sync_status)
        total = query.count()
        total_page = (
            total // page_size + 1 if total % page_size != 0 else total // page_size
        )
        response = query_with_page_and_order(
            query=query,
            page=page,
            page_size=page_size,
            order=order,
            order_field=order_field,
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "code": 0,
                "message": "查询成功",
                "total": total,
                "total_page": total_page,
                "page": page,
                "page_size": page_size,
                "order_field": order_field,
                "order": order,
                "data": [
                    BannerSchema.model_validate(item, from_attributes=True).model_dump()
                    for item in response.all()
                ],
            },
        )


@banner_router.post("/add_banner", summary="添加banner")
async def add_banner(
    name: str = Form(..., description="banner标题"),
    icon: UploadFile = File(..., description="banner封面"),
    banner_description: UploadFile = File(..., description="banner描述"),
    synchronize: bool = Form(False, description="同步状态"),
    online_status: bool = Form(False, description="上架状态"),
):
    """
    # 添加banner
    ## params
    - **name**: banner标题, 必填
    - **icon**: banner封面, 必填
    - **banner_description**: banner描述, 必填
    - **synchronize**: 同步状态, 可选, 默认False
    - **online_status**: 上架状态, 可选, 默认False
    """
    icon_filename = save_upload_image(icon)
    banner_description_filename = save_upload_file(banner_description)
    with SessionLocal() as db:
        banner = Banner(
            name=name,
            icon=icon_filename,
            introduction=banner_description_filename,
            synchronize=synchronize,
            status=online_status,
        )
        db.add(banner)
        db.flush()
        db.refresh(banner)
        db.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"code": 0, "message": "添加成功", "data": transform_schema(BannerSchema, banner)},
        )


@banner_router.put("/update_banner", summary="更新banner")
async def update_banner(
    id: int = Form(..., description="banner id"),
    name: Optional[str] = Form(None, description="banner标题"),
    icon: Optional[UploadFile] = File(None, description="banner封面"),
    banner_description: Optional[UploadFile] = File(None, description="banner描述"),
    synchronize: Optional[bool] = Form(None, description="同步状态"),
    online_status: Optional[bool] = Form(None, description="上架状态"),
):
    """
    # 更新banner
    ## params
    - **id**: banner id, 必填
    - **name**: banner标题, 可选
    - **icon**: banner封面, 可选
    - **banner_description**: banner描述, 可选
    - **synchronize**: 同步状态, 可选
    - **online_status**: 上架状态, 可选
    """
    with SessionLocal() as db:
        banner = db.query(Banner).filter(Banner.id == id).first()
        if not banner:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 1, "message": "banner不存在"},
            )
        if name:
            banner.name = name
        if icon:
            icon_filename = save_upload_image(icon)
            if banner.icon:
                delete_image(banner.icon)
            banner.icon = icon_filename
        if banner_description:
            banner_description_filename = save_upload_file(banner_description)
            if banner.introduction:
                delete_file(banner.introduction)
            banner.banner_description = banner_description_filename
        if synchronize is not None:
            banner.synchronize = synchronize
        if online_status is not None:
            banner.online_status = online_status
        db.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"code": 0, "message": "更新成功"},
        )


@banner_router.delete("/delete_banner", summary="删除banner")
async def delete_banner(
    id: int = Form(..., description="banner id"),
):
    """
    # 删除banner
    ## params
    - **id**: banner id, 必填
    """
    with SessionLocal() as db:
        banner = db.query(Banner).filter(Banner.id == id).first()
        if not banner:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 1, "message": "banner不存在"},
            )
        if banner.icon:
            delete_image(banner.icon)
        if banner.introduction:
            delete_file(banner.introduction)
        db.delete(banner)
        db.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"code": 0, "message": "删除成功"},
        )
