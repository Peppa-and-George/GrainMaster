import base64
from typing import Optional
import re

from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from fastapi import status, Body, Request, UploadFile, File, Depends
from jose import JWTError, ExpiredSignatureError

from auth import (
    get_user_by_request,
    get_base64_password,
)
from dependency.image import save_upload_image, delete_image
from schema.database import SessionLocal
from config import DEFAULT_AVATAR
from schema.tables import Client, ClientUser

no_auth_router = APIRouter()
auth_router = APIRouter()


def verify_phone_number(phone_number: str) -> bool:
    if re.match(r"^1[3-9]\d{9}$", phone_number):
        return True
    return False


@no_auth_router.post("/register", summary="注册用户")
async def register(
    phone_number: str = Body(..., description="手机号", embed=True),
    name: Optional[str] = Body(None, description="用户名", embed=True),
    password: str = Body(..., embed=True, description="密码"),
    b64encoded: bool = Body(False, embed=True, description="是否对密码进行base64编码"),
):
    """
    # 注册用户
    ## 参数
    - phone_number: str, 手机号
    - name: str, 用户名
    - password: str, 密码
    - b64encoded: bool, 是否对密码进行base64编码, 可选参数，默认为False
    """
    with SessionLocal() as db:
        if not verify_phone_number(phone_number):
            return JSONResponse(
                content={"code": 1, "message": "手机号格式错误"},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        if b64encoded:
            password = base64.b64decode(password).decode()
        user = (
            db.query(ClientUser).filter(ClientUser.phone_number == phone_number).first()
        )
        if user:
            return JSONResponse(
                content={"code": 1, "message": "用户已存在"},
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        # 查询后台系统中是否存在该用户
        client = db.query(Client).filter(Client.phone_number == phone_number).first()

        password = get_base64_password(password)
        user = ClientUser(
            name=name or phone_number,
            hashed_passwd=password,
            type=client.type if client else None,
            phone_number=phone_number,
            client_id=client.id if client else None,
            avatar=DEFAULT_AVATAR,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return JSONResponse(
            content={
                "code": 0,
                "message": "注册成功",
                "data": {
                    "id": user.id,
                    "phone_number": user.phone_number,
                    "name": user.name,
                    "type": user.type,
                },
            },
            status_code=status.HTTP_200_OK,
        )


@auth_router.put("/update_info", summary="更改用户信息")
async def update_info(
    req: Request,
    name: Optional[str] = Body(None, embed=True, description="用户名"),
    phone_number: Optional[str] = Body(None, embed=True, description="手机号"),
    password: Optional[str] = Body(None, embed=True, description="密码"),
    b64encoded: bool = Body(False, embed=True, description="是否对密码进行base64编码"),
):
    """
    # 更改用户信息
    ## 参数
    - token: str, 用户token
    - name: str, 用户名
    - password: str, 密码
    - b64encoded: bool, 是否对密码进行base64编码, 可选参数，默认为False
    """
    with SessionLocal() as db:
        # 验证token
        try:
            current_user = get_user_by_request(req)
        except ExpiredSignatureError:
            return JSONResponse(
                content={"code": 1, "message": "token已过期, 请重新登录"},
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
        except JWTError:
            return JSONResponse(
                content={"code": 1, "message": "检查到token被篡改, 请重新登录"},
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
        except Exception as e:
            return JSONResponse(
                content={"code": 1, "message": f"未知错误: {e}, 请重新登录"},
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
        user = (
            db.query(ClientUser).filter(ClientUser.id == current_user.get("id")).first()
        )
        if not user:
            return JSONResponse(
                content={"code": 1, "message": "用户不存在"},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        if not current_user.get("type"):
            return JSONResponse(
                content={"code": 1, "message": "用户类型错误, 该操作仅限于客户端用户"},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        if name:
            user.name = name
        if phone_number:
            if not verify_phone_number(phone_number):
                return JSONResponse(
                    content={"code": 1, "message": "手机号格式错误"},
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            user.phone_number = phone_number
        if password:
            if b64encoded:
                password = base64.b64decode(password).decode()
            user.hashed_passwd = get_base64_password(password)
        db.commit()
        db.refresh(user)
        return JSONResponse(
            content={
                "code": 0,
                "message": "更改成功",
                "data": {
                    "id": user.id,
                    "phone_number": user.phone_number,
                    "name": user.name,
                    "type": user.type,
                },
            },
            status_code=status.HTTP_200_OK,
        )


@auth_router.post("upload_avatar", summary="上传头像")
async def upload_avatar(
    request: Request, avatar: UploadFile = File(..., description="头像")
):
    """
    # 上传头像
    ## 参数
    - token: str, 用户token
    - avatar: str, 头像
    """
    with SessionLocal() as db:
        # 验证token
        try:
            current_user = get_user_by_request(request)
        except Exception as e:
            return JSONResponse(
                content={"code": 1, "message": "身份验证错误, 请重新登录"},
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
        if not current_user.get("type"):
            return JSONResponse(
                content={"code": 1, "message": "用户类型错误, 该操作仅限于客户端用户"},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        user = (
            db.query(ClientUser).filter(ClientUser.id == current_user.get("id")).first()
        )
        if not user:
            return JSONResponse(
                content={"code": 1, "message": "用户不存在"},
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        file_name = save_upload_image(avatar)
        if user.avatar:
            delete_image(user.avatar)
        user.avatar = file_name
        db.commit()
        db.refresh(user)
        return JSONResponse(
            content={
                "code": 0,
                "message": "更改成功",
                "data": {
                    "id": user.id,
                    "avatar": user.avatar,
                },
            },
            status_code=status.HTTP_200_OK,
        )
