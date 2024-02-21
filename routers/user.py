from typing import Literal

from fastapi import APIRouter, Query, status, Body
from fastapi.responses import JSONResponse
from models.base import UserInfoSchema
from auth import get_base64_password, verify_password

from schema.database import SessionLocal
from schema.common import page_with_order
from schema.tables import User


router = APIRouter()


@router.get("/get_users", summary="获取所有用户信息")
async def get_users_api(
    order_field: str = Query("id", description="排序字段"),
    order_desc: Literal["asc", "desc"] = Query("asc", description="是否降序"),
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
):
    """
    # 获取所有用户信息
    - **order_field**: 排序字段, 默认为id
    - **order_desc**: 是否降序, 默认为asc
    - **page**: 页码, 默认为1
    - **page_size**: 每页数量, 默认为10
    """
    with SessionLocal() as db:
        query = db.query(User)
        response = page_with_order(
            schema=UserInfoSchema,
            query=query,
            order_field=order_field,
            order=order_desc,
            page=page,
            page_size=page_size,
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"code": 0, "message": "success", "data": response},
        )


@router.post("/create_user", summary="创建用户")
async def create_user(
    username: str = Body(..., description="用户名"),
    password: str = Body(..., description="密码"),
    phone_number: str = Body(..., description="手机号"),
):
    """
    # 创建用户
    - **username**: 用户名
    - **password**: 密码
    - **phone_number**: 手机号
    """
    with SessionLocal() as db:
        user = db.query(User).filter(User.name == username).first()
        if user:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 1, "message": "用户已存在"},
            )
        user = User(
            name=username,
            phone_number=phone_number,
            hashed_passwd=get_base64_password(password),
        )
        db.add(user)
        db.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"code": 0, "message": "用户创建成功"},
        )


@router.post("/edit_user", summary="编辑用户")
async def edit_user(
    user_id: int = Body(..., description="用户ID"),
    username: str = Body(None, description="用户名"),
    phone_number: str = Body(None, description="手机号"),
):
    """
    # 编辑用户
    - **user_id**: 用户ID
    - **username**: 用户名
    - **phone_number**: 手机号
    """
    with SessionLocal() as db:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 1, "message": "用户不存在"},
            )
        if username:
            user.name = username
        if phone_number:
            user.phone_number = phone_number
        db.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"code": 0, "message": "用户编辑成功"},
        )


@router.post("/modify_password", summary="修改密码")
def modify_password(
    user_id: int = Body(..., description="用户ID"),
    old_password: str = Body(..., description="旧密码"),
    new_password: str = Body(..., description="新密码"),
):
    """
    # 修改密码
    - **user_id**: 用户ID
    - **old_password**: 旧密码
    - **new_password**: 新密码
    """
    with SessionLocal() as db:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 1, "message": "用户不存在"},
            )
        if not verify_password(old_password, user.hashed_passwd):
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 1, "message": "旧密码错误"},
            )
        user.hashed_passwd = get_base64_password(new_password)
        db.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"code": 0, "message": "密码修改成功"},
        )


@router.post("/reset_password", summary="重置密码")
def reset_password(
    user_id: int = Body(..., description="用户ID"),
    password: str = Body(..., description="密码"),
):
    """
    # 重置密码
    - **user_id**: 用户ID
    - **password**: 密码
    """
    with SessionLocal() as db:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 1, "message": "用户不存在"},
            )
        user.hashed_passwd = get_base64_password(password)
        db.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"code": 0, "message": "密码重置成功"},
        )


@router.delete("/delete_user", summary="删除用户")
def delete_user(user_id: int = Query(..., description="用户ID", examples=[1])):
    """
    # 删除用户
    - **user_id**: 用户ID
    """
    with SessionLocal() as db:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 1, "message": "用户不存在"},
            )
        db.delete(user)
        db.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"code": 0, "message": "用户删除成功"},
        )
