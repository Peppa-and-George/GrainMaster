from typing import Optional

from fastapi.routing import APIRouter
from fastapi import status, Form, UploadFile, File, Query
from fastapi.responses import JSONResponse
from schema.tables import CustomizedInformation
from schema.database import SessionLocal
from dependency.image import save_upload_image, delete_image

customized_information_router = APIRouter()


@customized_information_router.get("/get_customized_information", summary="获取定制信息")
async def get_customized_information():
    """
    获取定制信息
    """
    with SessionLocal() as session:
        customized_information = session.query(CustomizedInformation).all()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "code": 0,
                "message": "获取成功",
                "data": [
                    {
                        "id": item.id,
                        "introduction": item.introduction,
                        "icon": item.icon,
                    }
                    for item in customized_information
                ],
                "total": len(customized_information),
            },
        )


@customized_information_router.post("/create_customized_information", summary="创建定制信息")
async def create_customized_information(
    introduction: Optional[str] = Form(None, description="简介"),
    icon: Optional[UploadFile] = File(None, description="图标"),
):
    """
    创建定制信息
    # Form参数
    - **introduction**: 简介, str, 可选
    - **icon**: 工艺图片, files, 可选
    """
    filename = save_upload_image(icon) if icon else None
    with SessionLocal() as session:
        customized_information = CustomizedInformation(
            introduction=introduction, icon=filename
        )
        session.add(customized_information)
        session.commit()
        return JSONResponse(
            status_code=status.HTTP_201_CREATED, content={"code": 0, "message": "创建成功"}
        )


@customized_information_router.put("/update_customized_information", summary="更新定制信息")
async def update_customized_information(
    id: int,
    introduction: Optional[str] = Form(None, description="简介"),
    icon: Optional[UploadFile] = File(None, description="图标"),
):
    """
    更新定制信息
    # Form参数
    - **id**: 定制信息id, int, 必选
    - **introduction**: 简介, str, 可选
    - **icon**: 工艺图片, files, 可选
    """
    with SessionLocal() as session:
        customized_information = (
            session.query(CustomizedInformation).filter_by(id=id).first()
        )
        if not customized_information:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"code": 1, "message": "定制信息不存在"},
            )
        if icon:
            if customized_information.icon:
                delete_image(customized_information.icon)
            customized_information.icon = save_upload_image(icon)
        if introduction:
            customized_information.introduction = introduction
        session.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK, content={"code": 0, "message": "更新成功"}
        )


@customized_information_router.delete(
    "/delete_customized_information", summary="删除定制信息"
)
async def delete_customized_information(id: int = Query(..., description="定制信息id")):
    """
    删除定制信息
    # Form参数
    - **id**: 定制信息id, int, 必选
    """
    with SessionLocal() as session:
        customized_information = (
            session.query(CustomizedInformation).filter_by(id=id).first()
        )
        if not customized_information:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"code": 1, "message": "定制信息不存在"},
            )
        if customized_information.icon:
            delete_image(customized_information.icon)
        session.delete(customized_information)
        session.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK, content={"code": 0, "message": "删除成功"}
        )
