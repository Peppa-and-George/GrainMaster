from fastapi import APIRouter, HTTPException
from schema.curd import CURD
from models.base import User, ResStatus, UserInfo, UserRestPasswd
from auth import get_base64_password


curd = CURD()
router = APIRouter()


@router.get("/get_users_info", response_model=ResStatus, description="获取所有用户信息")
async def users():
    user = curd.user.get_users_info()
    res = [{"name": i.name, "phone_number": i.phone_number} for i in user]
    return {"data": res}


@router.post("/create_user", response_model=ResStatus, description="创建用户")
async def create_user(user: UserInfo):
    curd.user.create_user(user.name, user.phone_number, get_base64_password(user.password))
    return {}


@router.post("/edit_user", response_model=ResStatus, description="编辑用户")
async def edit_user(user: User):
    u = curd.user.get_user(user.name)
    if not u:
        u = curd.user.get_user(user.phone_number)
        if not u:
            raise HTTPException(status_code=404, detail="未查到该用户")

    curd.user.edit_user(user.name, user.phone_number)
    return {}


@router.post("/reset_password", response_model=ResStatus, description="重置密码")
def reset_password(user: UserRestPasswd):
    u = curd.user.get_user(user.name)
    if not u:
        return {"code": 1, "message": "未找到用户"}
    curd.user.reset_password(user.name, user.new_password)
    return {}
