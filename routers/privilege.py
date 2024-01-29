import uuid
from datetime import datetime
from typing import Literal, Union

from fastapi import APIRouter, HTTPException, status, Query, Body
from fastapi.responses import JSONResponse

from models.base import PrivilegeSchema, ClientPrivilegeRelationSchema
from schema.tables import Privilege, Client, ClientPrivilege
from schema.common import page_with_order
from schema.database import SessionLocal

privilege_router = APIRouter()


@privilege_router.get("/get_privileges", description="获取权益列表", summary="获取权益列表")
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


@privilege_router.get(
    "/get_privilege_client_relationship", description="获取客户的权益", summary="获取客户的权益"
)
async def get_privilege_client_relationship(
    client_name: str = Query("", description="客户名称"),
    privilege_number: str = Query("", description="权益编号"),
    effective_time: str = Query("", description="生效时间"),
    expired_date: str = Query("", description="过期时间"),
    order_field: str = Query("id", description="排序字段"),
    order: Literal["asc", "desc"] = Query("desc", description="排序类型"),
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
):
    try:
        with SessionLocal() as db:
            query = db.query(ClientPrivilege)
            if client_name:
                client = db.query(Client).filter_by(name=client_name).first()
                if not client:
                    return JSONResponse(
                        status_code=status.HTTP_200_OK,
                        content={"code": 1, "message": "客户不存在"},
                    )
                query = query.filter(ClientPrivilege.client_id == client.id)

            if privilege_number:
                query = query.filter(
                    ClientPrivilege.privilege_number == privilege_number
                )
            if effective_time:
                query = query.filter(
                    ClientPrivilege.effective_time
                    >= datetime.strptime(effective_time, "%Y-%m-%d %H:%M:%S")
                )
            if expired_date:
                query = query.filter(
                    ClientPrivilege.expired_date
                    <= datetime.strptime(expired_date, "%Y-%m-%d %H:%M:%S")
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


@privilege_router.get("/use_privilege_by_id", description="使用权益", summary="使用权益")
async def use_privilege_by_id(
    privilege_id: int = Query(..., description="权益ID"),
):
    try:
        with SessionLocal() as db:
            client_privilege = (
                db.query(ClientPrivilege)
                .filter(ClientPrivilege.id == privilege_id)
                .first()
            )
            if not client_privilege:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "message": "权益不存在"},
                )
            client_privilege.use_time = datetime.now()
            client_privilege.usable = False
            db.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"code": 0, "message": "使用成功"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@privilege_router.get(
    "/use_privilege_by_name", description="通过编号使用权益", summary="通过编号使用权益"
)
async def use_privilege_by_name(
    privilege_number: str = Query(..., description="权益编号"),
):
    try:
        with SessionLocal() as db:
            client_privilege = (
                db.query(ClientPrivilege)
                .filter(ClientPrivilege.privilege_number == privilege_number)
                .first()
            )
            if not client_privilege:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "message": "权益不存在"},
                )
            client_privilege.use_time = datetime.now()
            client_privilege.usable = False
            db.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"code": 0, "message": "使用成功"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@privilege_router.post(
    "/add_privilege_client_relationship", description="给客户添加权益", summary="给客户添加权益"
)
async def add_privilege_client_relationship(
    client_name: str = Body(..., description="客户名称"),
    privilege_name: str = Body(..., description="权益ID"),
    effective_time: str = Body(..., description="生效时间"),
    expired_date: str = Body(..., description="过期时间"),
):
    try:
        with SessionLocal() as db:
            client = db.query(Client).filter_by(name=client_name).first()
            if not client:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "message": "客户不存在"},
                )
            client_id = client.id
            privilege = db.query(Privilege).filter_by(name=privilege_name).first()
            if not privilege:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "message": "权益不存在"},
                )
            privilege_id = privilege.id
            effective_time = datetime.strptime(effective_time, "%Y-%m-%d %H:%M:%S")
            expired_date = datetime.strptime(expired_date, "%Y-%m-%d %H:%M:%S")
            client_privilege = ClientPrivilege(
                privilege_number=uuid.uuid4().hex,
                client_id=client_id,
                privilege_id=privilege_id,
                effective_time=effective_time,
                expired_date=expired_date,
            )
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


@privilege_router.post("/create_privilege", description="创建权益", summary="创建权益")
async def create_privilege(
    name: str = Body(..., description="权益名称"),
    privilege_type: str = Body("", description="权益类型"),
    description: str = Body("", description="权益描述"),
):
    try:
        with SessionLocal() as db:
            privilege = Privilege(
                name=name, description=description, privilege_type=privilege_type
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


@privilege_router.put("/update_privilege", description="更新权益", summary="更新权益")
async def update_privilege(
    id: int = Body(..., description="权益ID"),
    name: Union[str] = Body(None, description="权益名称"),
    description: Union[str] | None = Body(None, description="权益描述"),
):
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


@privilege_router.put(
    "/update_privilege_client_relationship", description="更新客户的权益", summary="更新客户的权益"
)
async def update_privilege_from_client(
    privilege_id: int = Body(..., description="权益ID"),
    effective_time: str = Body("", description="生效时间"),
    expired_date: str = Body("", description="过期时间"),
    use_time: str = Body("", description="使用时间"),
    usable: bool | None = Body(None, description="是否可用"),
):
    try:
        with SessionLocal() as db:
            client_privilege = (
                db.query(ClientPrivilege).filter(Privilege.id == privilege_id).first()
            )
            if not client_privilege:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "message": "权益不存在"},
                )
            if effective_time:
                client_privilege.effective_time = datetime.strptime(
                    effective_time, "%Y-%m-%d %H:%M:%S"
                )
            if expired_date:
                client_privilege.expired_date = datetime.strptime(
                    expired_date, "%Y-%m-%d %H:%M:%S"
                )
            if use_time:
                client_privilege.use_time = datetime.strptime(
                    use_time, "%Y-%m-%d %H:%M:%S"
                )
            if usable is not None:
                client_privilege.usable = usable
            db.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"code": 0, "message": "更新成功"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@privilege_router.delete("/delete_privilege", description="删除权益", summary="删除权益")
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
            db.commit()
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 0, "message": "删除成功"},
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@privilege_router.delete(
    "/delete_privilege_client_relationship", description="删除客户的权益", summary="删除客户的权益"
)
async def delete_privilege_from_client(
    privilege_id: int = Query(..., description="权益ID"),
):
    try:
        with SessionLocal() as db:
            client_privilege = (
                db.query(ClientPrivilege)
                .filter(ClientPrivilege.id == privilege_id)
                .first()
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
