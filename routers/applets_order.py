from datetime import datetime
from typing import List, Dict, Optional, Literal, Union

from fastapi import APIRouter, Query, status, Body
from fastapi.responses import JSONResponse

from schema.tables import AppletsOrder, AppletsOrderDetail, Product, Address, Client
from schema.common import page_with_order, transform_schema
from routers.order import generate_order_number
from schema.database import SessionLocal
from models.base import AppletsOrderSchema, AppletsOrderDetailSchema

applets_order_router = APIRouter()


@applets_order_router.get("/get_applets_orders", summary="批量获取小程序订单信息")
async def get_applets_orders_api(
    order: Union[str, int, None] = Query(None, description="订单号"),
    order_field_type: Literal["num", "id"] = Query("num", description="订单号字段类型"),
    client: Union[str, int, None] = Query(None, description="客户标识"),
    client_field_type: Literal["name", "id"] = Query("name", description="客户标识字段类型"),
    order_status: Optional[Literal["待支付", "已支付", "已完成"]] = Query(
        None, description="订单状态"
    ),
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    order_type: Literal["asc", "desc"] = Query("desc", description="排序方式"),
    order_field: Literal[
        "id", "order_number", "amounts_payable", "status", "payment_time"
    ] = Query("id", description="排序字段"),
):
    """
    # 批量获取小程序订单信息
    - order: 订单号， string, 可选
    - order_field_type: 订单号字段类型, string, 可选, 默认值: "num", 可选值: "num", "id"
    - client: 客户标识, string, 可选
    - client_field_type: 客户标识字段类型, string, 可选, 默认值: "name", 可选值: "name", "id"
    - order_status: 订单状态, string, 可选, 可选值: "待支付", "已支付", "已完成"
    - page: 页码, int, 可选, 默认值: 1
    - page_size: 每页数量, int, 可选, 默认值: 10
    - order_type: 排序方式, string, 可选, 默认值: "desc", 可选值: "asc", "desc"
    - order_field: 排序字段, string, 可选, 默认值: "id", 可选值: "id", "order_number", "amounts_payable", "status", "payment_time"
    """
    try:
        with SessionLocal() as db:
            query = db.query(AppletsOrder)
            if order:
                if order_field_type == "num":
                    query = query.filter(AppletsOrder.order_number == order)
                else:
                    query = query.filter(AppletsOrder.id == order)
            if client:
                if client_field_type == "name":
                    query = query.join(Client).filter(Client.name == client)
                else:
                    query = query.filter(AppletsOrder.client_id == client)
            if order_status:
                query = query.filter(AppletsOrder.status == order_status)
            response = page_with_order(
                AppletsOrderSchema, query, page, page_size, order_field, order_type
            )
            return JSONResponse(status_code=status.HTTP_200_OK, content=response)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"code": 1, "message": str(e)},
        )


@applets_order_router.get("/get_applets_order_details", summary="获取小程序订单信息")
async def get_applets_order_details_api(
    order: Union[str, int, None] = Query(None, description="订单号"),
    field_type: Literal["num", "id"] = Query("num", description="订单号字段类型"),
):
    """
    # 获取小程序订单信息
    - order: 订单号， string, 可选
    - field_type: 订单号字段类型, string, 可选, 默认值: "num", 可选值: "num", "id"
    """
    try:
        with SessionLocal() as db:
            if field_type == "num":
                order = (
                    db.query(AppletsOrderDetail)
                    .filter(AppletsOrder.order_number == order)
                    .first()
                )
            else:
                order = (
                    db.query(AppletsOrderDetail)
                    .filter(AppletsOrderDetail.id == order)
                    .first()
                )
            if not order:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "message": "订单不存在"},
                )
            data = transform_schema(AppletsOrderDetailSchema, order)

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 0, "message": "查询成功", "data": data},
            )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"code": 1, "message": str(e)},
        )


@applets_order_router.post("/create_applets_order", summary="创建小程序订单")
async def create_applets_order_api(
    client_id: int = Body(..., description="客户id"),
    address_id: int = Body(..., description="地址id"),
    items: List[Dict[str, int]] = Body(
        ...,
        description="订单详情",
        examples=[
            [{"product_id": 1, "quantity": 10}, {"product_id": 2, "quantity": 20}]
        ],
    ),
):
    """
    # 创建小程序订单
    - client_id: 客户id, int, 必填
    - address_id: 地址id, int, 必填
    - items: 订单详情, list, 必填
    """
    try:
        with SessionLocal() as db:
            address = (
                db.query(Address)
                .join(Client, Address.client_id == Client.id)
                .filter(Address.id == address_id, Client.id == client_id)
                .first()
            )
            if not address:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "message": "客户或地址不存在"},
                )
            order = AppletsOrder(
                order_number=generate_order_number(),
                status="待支付",
            )
            order.address = address
            order.client = address.client

            amounts_payable = 0

            for item in items:
                product = (
                    db.query(Product).filter(Product.id == item["product_id"]).first()
                )
                if not product:
                    return JSONResponse(
                        status_code=status.HTTP_200_OK,
                        content={"code": 1, "message": f"商品{item['product_id']}不存在"},
                    )
                # 验证库存
                if product.amount < item["quantity"]:
                    return JSONResponse(
                        status_code=status.HTTP_200_OK,
                        content={
                            "code": 1,
                            "message": f"商品{product.name}库存不足",
                        },
                    )

                amounts_payable += product.price * item["quantity"]
                detail = AppletsOrderDetail(
                    quantity=item["quantity"], price=product.price
                )
                detail.product = product
                order.details.append(detail)
            order.amounts_payable = amounts_payable
            db.add(order)
            db.commit()
            return JSONResponse(
                status_code=status.HTTP_200_OK, content={"code": 0, "message": "创建成功"}
            )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"code": 1, "message": str(e)},
        )


@applets_order_router.post("/pay_applets_order", summary="支付小程序订单")
async def pay_applets_order_api(
    order: Union[int, str] = Body(..., description="订单号"),
    field_type: Literal["num", "id"] = Query("num", description="订单号字段类型"),
    payment_method: Optional[str] = Body(None, description="支付方式"),
    payment_amount: Optional[float] = Body(None, description="支付金额"),
    payment_time: Optional[str] = Body(
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        description="支付时间",
        examples=["2021-01-01 00:00:00"],
    ),
):
    """
    # 支付小程序订单
    - order: 订单号， string, 必填
    - field_type: 订单号字段类型, string, 可选, 默认值: "num", 可选值: "num", "id"
    - payment_method: 支付方式, string, 可选
    - payment_amount: 支付金额, float, 可选, 默认值: 订单应付金额
    - payment_time: 支付时间, string, 可选, 默认值: 当前时间
    """
    try:
        with SessionLocal() as db:
            if field_type == "num":
                order = (
                    db.query(AppletsOrder)
                    .filter(AppletsOrder.order_number == order)
                    .first()
                )
            else:
                order = db.query(AppletsOrder).filter(AppletsOrder.id == order).first()
            if not order:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "message": "订单不存在"},
                )
            if order.status != "待支付":
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "message": "订单支付状态不正确"},
                )
            order.status = "已支付"
            order.payment_method = payment_method
            if payment_amount:
                order.payment_amount = payment_amount
            else:
                order.payment_amount = order.amounts_payable
            order.payment_time = datetime.strptime(payment_time, "%Y-%m-%d %H:%M:%S")
            db.commit()
            return JSONResponse(
                status_code=status.HTTP_200_OK, content={"code": 0, "message": "支付成功"}
            )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"code": 1, "message": str(e)},
        )


@applets_order_router.put("/update_applets_order_address", summary="更新小程序订单收获地址")
def update_applets_order_address_api(
    order: Union[int, str] = Body(..., description="订单id"),
    field_type: Literal["num", "id"] = Query("num", description="订单号字段类型"),
    address_id: int = Body(..., description="地址id"),
):
    """
    # 更新小程序订单收获地址
    - order: 订单id, int, 必填
    - field_type: 订单号字段类型, string, 可选, 默认值: "num", 可选值: "num", "id"
    - address_id: 地址id, int, 可选
    """
    try:
        with SessionLocal() as db:
            if field_type == "num":
                order = (
                    db.query(AppletsOrder)
                    .filter(AppletsOrder.order_number == order)
                    .first()
                )
            else:
                order = db.query(AppletsOrder).filter(AppletsOrder.id == order).first()
            if not order:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "message": "订单不存在"},
                )

            address = (
                db.query(Address)
                .join(Client)
                .filter(Address.id == address_id, Client.id == order.client_id)
                .first()
            )
            if not address:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "message": "当前客户不存在该地址"},
                )
            order.address = address
            db.commit()
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 0, "message": "更新成功"},
            )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"code": 1, "message": str(e)},
        )


@applets_order_router.put("/complete_applets_order", summary="完成小程序订单")
def complete_applets_order_api(
    order: int = Body(..., description="订单id"),
    field_type: Literal["num", "id"] = Query("num", description="订单号字段类型"),
):
    """
    # 完成小程序订单
    - order: 订单id, int, 必填
    - field_type: 订单号字段类型, string, 可选, 默认值: "num", 可选值: "num", "id"
    """
    try:
        with SessionLocal() as db:
            if field_type == "num":
                order = (
                    db.query(AppletsOrder)
                    .filter(AppletsOrder.order_number == order)
                    .first()
                )
            else:
                order = db.query(AppletsOrder).filter(AppletsOrder.id == order).first()
            if not order:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "message": "订单不存在"},
                )
            if order.status != "已支付":
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "message": "只能完成已支付订单"},
                )
            order.status = "已完成"
            db.commit()
            return JSONResponse(
                status_code=status.HTTP_200_OK, content={"code": 0, "message": "完成成功"}
            )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"code": 1, "message": str(e)},
        )


@applets_order_router.delete("/delete_applets_order", summary="删除小程序订单")
def delete_applets_order_api(
    order: int = Body(..., description="订单id"),
    field_type: Literal["num", "id"] = Query("num", description="订单号字段类型"),
):
    """
    # 删除小程序订单
    - order: 订单id, int, 必填
    - field_type: 订单号字段类型, string, 可选, 默认值: "num", 可选值: "num", "id"
    """
    try:
        with SessionLocal() as db:
            if field_type == "num":
                order = (
                    db.query(AppletsOrder)
                    .filter(AppletsOrder.order_number == order)
                    .first()
                )
            else:
                order = db.query(AppletsOrder).filter(AppletsOrder.id == order).first()
            if not order:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "message": "订单不存在"},
                )
            db.delete(order)
            db.commit()
            return JSONResponse(
                status_code=status.HTTP_200_OK, content={"code": 0, "message": "删除成功"}
            )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"code": 1, "message": str(e)},
        )
