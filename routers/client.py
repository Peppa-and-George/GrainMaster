import re
from datetime import datetime
from typing import Literal
import uuid

from fastapi import APIRouter, Query, HTTPException, status, Body, Request
from fastapi.responses import JSONResponse

from schema.common import page_with_order, query_with_page_and_order, transform_schema
from schema.tables import Client, Address, ClientUser
from schema.database import SessionLocal
from models.base import ClientSchema, AddressSchema, OrderSchema
from auth import get_base64_password

from auth import decode_token

client_router = APIRouter()


def verify_phone_number(phone_number: str) -> bool:
    if re.match(r"^1[3-9]\d{9}$", phone_number):
        return True
    return False


@client_router.get("/get_clients", summary="获取客户列表")
async def get_clients(
    fuzzy: bool = Query(False, description="模糊搜索"),
    client_type: str | None = Query(None, description="客户类型"),
    name: str | None = Query(None, description="账号名称"),
    activate: bool | None = Query(None, description="激活状态"),
    order_field: str = Query("id", description="排序字段"),
    order: Literal["asc", "desc"] = Query("desc", description="排序类型"),
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
):
    """
    # 获取客户列表
    ## 请求体字段：
    - **client_type**: 客户类型
    - **name**: 账号名称
    - **activate**: 激活状态
    - **order_field**: 排序字段
    - **order**: 排序类型
    - **page**: 页码
    - **page_size**: 每页数量

    ## 返回字段：
    - **id**: 客户ID
    - **type**: 客户类型
    - **account**: 客户账号
    - **name**: 客户名称
    - **category**: 客户类别
    - **activate**: 客户状态
    - **create_time**: 创建时间
    - **update_time**: 更新时间
    - **delete_time**: 删除时间
    """
    try:
        with SessionLocal() as db:
            query = db.query(Client).filter(Client.is_deleted == False)

            if client_type:
                query = query.filter(Client.type == client_type)
            if name:
                if fuzzy:
                    query = query.filter(Client.name.like(f"%{name}%"))
                else:
                    query = query.filter(Client.name == name)
            if activate is not None:
                query = query.filter(Client.activate == activate)

            total = query.count()
            total_page = (
                total // page_size + 1 if total % page_size != 0 else total // page_size
            )
            query = query_with_page_and_order(
                query, page, page_size, order_field, order
            )
            clients = query.all()
            data = []
            for client in clients:
                client_dict = ClientSchema.model_validate(
                    client, from_attributes=True
                ).model_dump()
                client_dict.update({"order_number": client.orders.count()})
                client_dict.update(
                    {"order": transform_schema(OrderSchema, client.orders)}
                )
                data.append(client_dict)

            response = {
                "total": total,
                "total_page": total_page,
                "page": page,
                "page_size": page_size,
                "order_field": order_field,
                "order": order,
                "data": data,
                **{
                    "code": 0,
                    "message": "查询成功",
                },
            }

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=response,
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@client_router.get("/get_client_addresses", summary="根据客户ID获取客户地址列表")
async def get_client_addresses(
    client_id: int = Query(..., description="客户ID"),
    order_field: str = Query("id", description="排序字段"),
    order: Literal["asc", "desc"] = Query("desc", description="排序类型"),
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
):
    """
    # 根据客户ID获取客户地址列表
    ## 请求体字段：
    - **client_id**: 客户ID
    - **order_field**: 排序字段
    - **order**: 排序类型
    - **page**: 页码
    - **page_size**: 每页数量

    ## 返回字段：
    - **id**: 地址ID
    - **client_id**: 客户ID
    - **name**: 客户名称
    - **phone_num**: 客户手机号
    - **region**: 客户地区
    - **detail_address**: 客户详细地址
    - **create_time**: 创建时间
    - **update_time**: 更新时间
    """
    try:
        with SessionLocal() as db:
            query = db.query(Address).filter(Address.client_id == client_id)
            response = page_with_order(
                schema=AddressSchema,
                query=query,
                page=page,
                page_size=page_size,
                order_field=order_field,
                order=order,
            )

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=response,
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@client_router.post("/add_client", summary="添加客户")
async def add_client(
    request: Request,
    client_type: str = Body(..., description="客户类型"),
    name: str = Body(..., description="账号名"),
    phone_number: str = Body(..., description="绑定手机号"),
    region: str = Body(..., description="地区"),
    address: str = Body(..., description="地址"),
    signing_people: str | None = Body(None, description="签约人"),
    signing_phone: str | None = Body(None, description="签约人手机号"),
    category: str = Body(default="", description="客户类别"),
    activate: bool = Body(False, description="客户状态"),
):
    """
    # 添加客户
    ## 请求体字段：
    - **client_type**: 客户类型
    - **name**: 账号名
    - **phone_number**: 绑定手机号
    - **region**: 地区
    - **address**: 地址
    - **category**: 客户类别
    - signing_people: 签约人, 可选
    - signing_phone: 签约人手机号, 可选
    - **activate**: 客户是否激活，bool类型
    """
    # validate phone number
    if not verify_phone_number(phone_number):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"code": 1, "message": "手机号格式错误"},
        )

    if signing_people is None or signing_phone is None:
        token = request.headers.get("Authorization")
        user_info = decode_token(token.replace("Bearer ", ""))
        signing_people = user_info.get("sub")
        signing_phone = user_info.get("phone_number")
    try:
        with SessionLocal() as db:
            client = Client(
                type=client_type,
                account=str(uuid.uuid4()),
                name=name,
                category=category,
                activate=activate,
                is_deleted=False,
                phone_number=phone_number,
                signing_people=signing_people,
                signing_phone=signing_phone,
                region=region,
                address=address,
            )
            client_user = (
                db.query(ClientUser)
                .filter(ClientUser.phone_number == phone_number)
                .first()
            )
            if not client_user:
                client_user = ClientUser(
                    name=name,
                    phone_number=phone_number,
                    hashed_passwd=get_base64_password(phone_number[-6:]),
                    type=client_type,
                    avatar="default.png",
                )
            client.client_user = client_user
            db.add(client)
            db.flush()
            db.refresh(client)
            db.commit()
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "code": 0,
                    "message": "添加成功",
                    "data": transform_schema(ClientSchema, client),
                },
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@client_router.post("/add_client_address", summary="添加客户地址")
async def add_client_address(
    client_id: int = Body(..., description="客户ID"),
    name: str = Body(..., description="姓名"),
    phone_number: str = Body(..., description="手机号"),
    region: str = Body(..., description="地区"),
    address: str = Body(..., description="地址"),
):
    """
    # 添加客户地址
    ## 请求体字段：
    - **client_id**: 客户ID
    - **name**: 姓名
    - **phone_number**: 手机号
    - **region**: 地区
    - **address**: 地址
    """
    try:
        with SessionLocal() as db:
            address = Address(
                client_id=client_id,
                name=name,
                phone_num=phone_number,
                region=region,
                detail_address=address,
            )
            db.add(address)
            db.flush()
            db.refresh(address)
            db.commit()
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "code": 0,
                    "message": "添加成功",
                    "data": transform_schema(AddressSchema, address),
                },
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@client_router.put("/update_client", summary="修改客户信息")
async def update_client(
    client_id: int = Body(..., description="客户ID"),
    client_type: str | None = Body(None, description="客户类型"),
    account: str | None = Body(None, description="客户账号"),
    name: str | None = Body(None, description="账号名"),
    phone_number: str | None = Body(None, description="绑定手机号"),
    signing_people: str | None = Body(None, description="签约人"),
    signing_phone: str | None = Body(None, description="签约人手机号"),
    category: str | None = Body(None, description="客户类别"),
    activate: bool | None = Body(None, description="客户状态"),
    region: str | None = Body(None, description="地区"),
    address: str | None = Body(None, description="地址"),
):
    """
    # 修改客户信息
    ## 请求体字段：
    - **client_id**: 客户ID
    - **client_type**: 客户类型
    - **account**: 客户账号
    - **name**: 账号名
    - **phone_number**: 绑定手机号
    - **signing_people**: 签约人
    - **signing_phone**: 签约人手机号
    - **category**: 客户类别
    - **activate**: 客户是否激活，bool类型
    - **region**: 地区
    - **address**: 地址
    """
    try:
        with SessionLocal() as db:
            client = db.query(Client).filter(Client.id == client_id).first()
            if not client:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="客户不存在"
                )
            if client_type:
                client.type = client_type
            if account:
                client.account = account
            if name:
                client.name = name
            if category:
                client.category = category
            if activate is not None:
                client.activate = activate
            if phone_number:
                client.phone_number = phone_number
            if signing_people:
                client.signing_people = signing_people
            if signing_phone:
                client.signing_phone = signing_phone
            if region:
                client.region = region
            if address:
                client.address = address

            db.commit()
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 0, "message": "修改成功"},
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@client_router.put("/update_client_address", summary="修改客户地址信息")
async def update_client_address(
    address_id: int = Body(..., description="地址ID"),
    name: str | None = Body(None, description="姓名"),
    phone_number: str | None = Body(None, description="手机号"),
    region: str | None = Body(None, description="地区"),
    address: str | None = Body(None, description="地址"),
):
    """
    # 修改客户地址信息
    ## 请求体字段：
    - **address_id**: 地址ID
    - **name**: 姓名, 可选
    - **phone_number**: 手机号, 可选
    - **region**: 地区, 可选
    - **address**: 地址, 可选
    """
    try:
        with SessionLocal() as db:
            address_object = db.query(Address).filter(Address.id == address_id).first()
            if not address_object:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="地址不存在"
                )
            if name:
                address_object.name = name
            if phone_number:
                address_object.phone_num = phone_number
            if region:
                address_object.region = region
            if address:
                address_object.detail_address = address
            db.commit()
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 0, "message": "修改成功"},
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@client_router.delete("/delete_client", summary="删除客户")
async def delete_client(
    client_id: int = Query(..., description="客户ID"),
):
    try:
        with SessionLocal() as db:
            client = db.query(Client).filter(Client.id == client_id).first()
            if not client:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="客户不存在"
                )
            client.is_deleted = True
            client.delete_time = datetime.now()
            db.commit()
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 0, "message": "删除成功"},
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@client_router.delete("/delete_client_address", summary="删除客户地址")
async def delete_client_address(
    address_id: int = Query(..., description="地址ID"),
):
    try:
        with SessionLocal() as db:
            address = db.query(Address).filter(Address.id == address_id).first()
            if not address:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="地址不存在"
                )
            db.delete(address)
            db.commit()
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 0, "message": "删除成功"},
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
