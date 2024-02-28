import uuid
from datetime import datetime
from typing import Literal, Union, Optional

from fastapi import APIRouter, HTTPException, status, Query, Body
from fastapi.responses import JSONResponse

from models.base import PrivilegeSchema, ClientPrivilegeRelationSchema
from schema.tables import Privilege, Client, ClientPrivilege, PrivilegeUsage
from schema.common import page_with_order
from schema.database import SessionLocal

privilege_router = APIRouter()


def generate_privilege_number():
    return uuid.uuid4().hex


@privilege_router.get("/get_privileges", summary="获取权益列表")
async def get_privileges(
    order_field: str = Query("id", description="排序字段"),
    order: Literal["asc", "desc"] = Query("desc", description="排序类型"),
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
):
    try:
        with SessionLocal() as db:
            query = db.query(Privilege).filter(Privilege.deleted == False)
            data = page_with_order(
                schema=PrivilegeSchema,
                query=query,
                page=page,
                page_size=page_size,
                order_field=order_field,
                order=order,
            )
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=data,
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@privilege_router.get("/get_privilege_client_relationship", summary="获取客户的权益")
async def get_privilege_client_relationship(
    client: Optional[str] = Query(None, description="客户标识"),
    client_file_type: Literal["name", "id"] = Query("id", description="客户标识类型"),
    expired: Optional[bool] = Query(None, description="是否过期"),
    use_status: Optional[Literal["unused", "partially_used", "used_up"]] = Query(
        None, description="使用状态, unused: 未使用, partially_used: 部分使用, used_up: 已使用完"
    ),
    privilege_number: Optional[str] = Query(None, description="权益编号"),
    privilege_name: Optional[str] = Query(None, description="权益名称"),
    start_time: Optional[str] = Query(None, description="开始时间"),
    end_time: Optional[str] = Query(None, description="结束时间"),
    order_field: str = Query("id", description="排序字段"),
    order: Literal["asc", "desc"] = Query("desc", description="排序类型"),
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
):
    try:
        with SessionLocal() as db:
            query = db.query(ClientPrivilege)
            if client:
                if client_file_type == "name":
                    query = query.join(Client).filter(Client.name == client)
                else:
                    query = query.filter(Client.id == client)
            if expired is not None:
                if expired:
                    query = query.filter(ClientPrivilege.expired_date > datetime.now())
                else:
                    query = query.filter(ClientPrivilege.expired_date < datetime.now())
            if use_status:
                if use_status == "unused":
                    query = query.filter(
                        ClientPrivilege.used_amount == 0,
                        ClientPrivilege.amount == ClientPrivilege.unused_amount,
                    )
                elif use_status == "partially_used":
                    query = query.filter(
                        ClientPrivilege.unused_amount > 0,
                        ClientPrivilege.unused_amount < ClientPrivilege.amount,
                    )
                else:
                    query = query.filter(
                        ClientPrivilege.unused_amount == 0,
                        ClientPrivilege.amount == ClientPrivilege.used_amount,
                    )
            if privilege_number or privilege_name:
                query = query.join(Privilege)
            if privilege_number:
                query = query.filter(Privilege.privilege_number == privilege_number)
            if privilege_name:
                query = query.filter(Privilege.name == privilege_name)
            if start_time:
                query = query.filter(
                    ClientPrivilege.effective_time
                    >= datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
                )
            if end_time:
                query = query.filter(
                    ClientPrivilege.expired_date
                    <= datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
                )
            data = page_with_order(
                schema=ClientPrivilegeRelationSchema,
                query=query,
                page=page,
                page_size=page_size,
                order_field=order_field,
                order=order,
            )
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=data,
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@privilege_router.get("/use_privilege", summary="使用权益")
async def use_privilege(
    privilege: Union[int, str] = Query(..., description="权益标识"),
    field_type: Literal["name", "id"] = Query("id", description="权益标识类型"),
    amount: Optional[int] = Query(1, description="使用数量", examples=[1]),
):
    """
    # 使用权益
    - privilege: 用户权益标识
    - field_type: 权益标识类型, 可选值: name, id
    - amount: 使用数量, 选填, 默认1
    """
    try:
        with SessionLocal() as db:
            if field_type == "name":
                privilege_client_relation = (
                    db.query(ClientPrivilege)
                    .join(Privilege, ClientPrivilege.privilege_id == Privilege.id)
                    .filter(Privilege.name == privilege)
                    .first()
                )
            else:
                privilege_client_relation = (
                    db.query(ClientPrivilege)
                    .join(Privilege, ClientPrivilege.privilege_id == Privilege.id)
                    .filter(ClientPrivilege.id == privilege)
                    .first()
                )
            if not privilege_client_relation:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "message": "权益不存在"},
                )
            if privilege_client_relation.unused_amount < amount:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "message": "权益数量不足"},
                )
            privilege_client_relation.unused_amount -= amount
            privilege_client_relation.used_amount += amount
            usage = PrivilegeUsage(used_amount=amount, used_time=datetime.now())
            usage.client_privilege = privilege_client_relation
            usage.privilege = privilege_client_relation.privilege
            usage.client = privilege_client_relation.client
            db.add(usage)
            db.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"code": 0, "message": "使用成功"},
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@privilege_router.post("/add_privilege_to_clients", summary="给客户添加权益")
async def add_privilege_client_relationship(
    clients: str = Body(..., description="客户标识, 多个客户用英文逗号隔开"),
    field_type: Literal["name", "id"] = Body("id", description="客户标识类型"),
    privilege_name: str = Body(..., description="权益ID"),
    privilege_type: str = Body(..., description="权益类型"),
    privilege_description: str = Body("", description="权益描述"),
    effective_time: str = Body(
        ..., description="生效时间", examples=["2021-01-01 00:00:00"]
    ),
    expired_date: str = Body(..., description="过期时间", examples=["2021-12-31 23:59:59"]),
    amount: int = Body(1, description="数量", examples=[1]),
):
    """
    # 给客户添加权益
    - clients: 客户标识, 多个客户用英文逗号隔开
    - field_type: 客户标识类型, 可选值: name, id
    - privilege_name: 权益名称
    - privilege_type: 权益类型
    - privilege_description: 权益描述, 选填
    - effective_time: 生效时间
    - expired_date: 过期时间
    - amount: 数量, 选填, 默认1
    """
    try:
        with SessionLocal() as db:
            privilege = (
                db.query(Privilege)
                .filter(Privilege.name == privilege_name and Privilege.deleted == False)
                .first()
            )
            if not privilege:
                # 创建权益
                privilege = Privilege(
                    name=privilege_name,
                    description=privilege_description,
                    privilege_type=privilege_type,
                    privilege_number=generate_privilege_number(),
                )
            clients = clients.split(",")
            for client in clients:
                if field_type == "name":
                    client_obj = db.query(Client).filter(Client.name == client).first()
                else:
                    client_obj = db.query(Client).filter(Client.id == client).first()
                if not client:
                    return JSONResponse(
                        status_code=status.HTTP_200_OK,
                        content={"code": 1, "message": f"客户{field_type}:{client}不存在"},
                    )
                client_privilege = ClientPrivilege(
                    client_id=client_obj.id,
                    privilege_id=privilege.id,
                    effective_time=datetime.strptime(
                        effective_time, "%Y-%m-%d %H:%M:%S"
                    ),
                    expired_date=datetime.strptime(expired_date, "%Y-%m-%d %H:%M:%S"),
                    amount=amount,
                    used_amount=0,
                    unused_amount=amount,
                )
                client_privilege.privilege = privilege
                db.add(client_privilege)
            db.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"code": 0, "message": "添加成功"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@privilege_router.post("/create_privilege", summary="创建权益")
async def create_privilege(
    name: str = Body(..., description="权益名称"),
    privilege_type: str = Body("", description="权益类型"),
    description: str = Body("", description="权益描述"),
):
    """
    # 创建权益
    - name: 权益名称
    - privilege_type: 权益类型
    - description: 权益描述, 选填
    """
    try:
        with SessionLocal() as db:
            privilege = Privilege(
                name=name,
                description=description,
                privilege_type=privilege_type,
                privilege_number=generate_privilege_number(),
            )
            db.add(privilege)
            db.commit()
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 0, "message": "创建成功"},
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@privilege_router.put("/update_privilege", summary="更新权益")
async def update_privilege(
    id: int = Body(..., description="权益ID"),
    name: Union[str] = Body(None, description="权益名称"),
    description: Union[str] | None = Body(None, description="权益描述"),
):
    """
    # 更新权益
    - id: 权益ID
    - name: 权益名称, 选填
    - description: 权益描述, 选填
    """
    try:
        with SessionLocal() as db:
            privilege = db.query(Privilege).filter(Privilege.id == id).first()
            if not privilege:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "message": "权益不存在"},
                )
            if name:
                privilege.name = name
            if description:
                privilege.description = description
            db.commit()
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 0, "message": "更新成功"},
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@privilege_router.put("/update_privilege_client_relationship", summary="更新客户的权益")
async def update_privilege_from_client(
    id: int = Body(..., description="客户对应权益ID"),
    effective_time: str = Body(
        "", description="生效时间", examples=["2021-01-01 00:00:00"]
    ),
    expired_date: str = Body("", description="过期时间", examples=["2021-12-31 23:59:59"]),
):
    """
    # 更新客户的权益
    - id: 客户对应权益ID
    - effective_time: 生效时间, 选填
    - expired_date: 过期时间, 选填
    """
    try:
        with SessionLocal() as db:
            client_privilege = (
                db.query(ClientPrivilege).filter(ClientPrivilege.id == id).first()
            )
            if effective_time:
                client_privilege.effective_time = datetime.strptime(
                    effective_time, "%Y-%m-%d %H:%M:%S"
                )
            if expired_date:
                client_privilege.expired_date = datetime.strptime(
                    expired_date, "%Y-%m-%d %H:%M:%S"
                )
            db.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"code": 0, "message": "更新成功"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@privilege_router.put("/modify_privilege_amount", summary="更新客户的权益数量")
async def modify_privilege_amount(
    id: int = Body(..., description="客户对应权益ID"),
    amount: int = Body(1, description="数量", examples=[1]),
    operator: Literal["add", "sub"] = Body("add", description="操作类型"),
):
    """
    # 更新客户的权益数量
    - id: 客户对应权益ID
    - amount: 数量
    """
    try:
        with SessionLocal() as db:
            client_privilege = (
                db.query(ClientPrivilege).filter(ClientPrivilege.id == id).first()
            )
            if operator == "add":
                client_privilege.amount += amount
                client_privilege.unused_amount += amount
            else:
                if client_privilege.amount < amount:
                    return JSONResponse(
                        status_code=status.HTTP_200_OK,
                        content={"code": 1, "message": f"权益数量不足{amount}"},
                    )
                client_privilege.amount -= amount
                client_privilege.unused_amount = max(
                    client_privilege.unused_amount - amount, 0
                )
            db.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"code": 0, "message": "更新成功"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@privilege_router.delete("/delete_privilege", summary="删除权益")
async def delete_privilege(id: int = Query(..., description="权益ID")):
    try:
        with SessionLocal() as db:
            privilege = db.query(Privilege).filter(Privilege.id == id).first()
            if not privilege:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "message": "权益不存在"},
                )
            privilege.deleted = True
            privilege.name = f"{privilege.name}_deleted"
            db.commit()
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 0, "message": "删除成功"},
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@privilege_router.delete("/delete_privilege_client_relationship", summary="删除客户的权益")
async def delete_privilege_from_client(
    id: int = Query(..., description="客户对应权益ID"),
):
    try:
        with SessionLocal() as db:
            client_privilege = (
                db.query(ClientPrivilege).filter(ClientPrivilege.id == id).first()
            )
            if not client_privilege:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "message": "权益不存在"},
                )
            client_privilege.deleted()
            db.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"code": 0, "message": "删除成功"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
