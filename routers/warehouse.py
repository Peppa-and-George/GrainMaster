from datetime import datetime
from typing import Literal, Optional, Union

from fastapi import APIRouter, Query, status, Body, HTTPException, Request
from fastapi.responses import JSONResponse

from schema.tables import Transport, Plan, Location, Warehouse, Order, Product, Quality
from schema.common import page_with_order
from schema.database import SessionLocal
from models.base import WarehouseSchema

warehouse_router = APIRouter()


@warehouse_router.get("/get_warehouse", summary="获取仓库信息")
async def get_warehouse(
    year: int = Query(None, description="年份"),
    batch: int = Query(None, description="批次"),
    location_name: str = Query(None, description="基地名称"),
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    order: Literal["asc", "desc"] = Query("asc", description="排序"),
    order_field: str = Query("id", description="排序字段"),
):
    """
    # 获取仓储加工信息
    ## params
    - **year**: 年份, 可选
    - **batch**: 批次, 可选
    - **location_name**: 基地名称, 可选
    - **page**: 页码, 从1开始, 可选
    - **page_size**: 分页大小，默认10，范围1-100, 可选
    - **order**: 排序方式, 可选
    - **search**: 搜索, 可选
    """
    try:
        with SessionLocal() as db:
            query = db.query(Warehouse).join(Plan, Plan.id == Warehouse.plan_id)
            if year:
                query = query.filter(Plan.year == year)
            if batch:
                query = query.filter(Plan.batch == batch)
            if location_name:
                location = (
                    db.query(Location).filter(Location.name == location_name).first()
                )
                if not location:
                    return JSONResponse(
                        status_code=status.HTTP_200_OK,
                        content={"code": 1, "message": "位置不存在"},
                    )
                query = query.filter(Plan.location_id == location.id)
            response = page_with_order(
                schema=WarehouseSchema,
                query=query,
                page=page,
                page_size=page_size,
                order=order,
                order_field=order_field,
            )
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=response,
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取仓库信息失败, {e}",
        )


@warehouse_router.post("/add_warehouse", summary="添加仓库信息")
async def add_warehouse(
    req: Request,
    plan_id: int = Body(..., description="计划ID"),
    product_name: Optional[str] = Body(
        None, description="产品名称", examples=["大豆油", "花生油"]
    ),
    unit: Optional[float] = Body(None, description="规格", examples=[4.8, 10]),
    amount: Optional[float] = Body(None, description="数量", examples=[100, 200]),
    product_id: Optional[int] = Body(None, description="产品ID"),
    order: Union[int, str] = Body(..., description="订单"),
    order_field_type: Literal["id", "num"] = Body("id", description="排序"),
    operate_date: Optional[str] = Body(None, description="计划操作日期"),
    feeding_place: Optional[str] = Body(None, description="投料口转运"),
    feeding_warehouse: Optional[str] = Body(None, description="投料仓转运地点"),
    feeding: Optional[str] = Body(None, description="投料"),
    press: Optional[str] = Body(None, description="压榨"),
    refine: Optional[str] = Body(None, description="精炼"),
    sorting: Optional[str] = Body(None, description="分装"),
    warehousing: Optional[str] = Body(None, description="入库"),
    product_warehousing: Optional[str] = Body(None, description="成品入库地点"),
    notices: Optional[str] = Body(None, description="备注"),
):
    """
    # 添加仓库信息，product_name和product_id必须存在一个, 当填入product_name时，会自动创建商品信息,填入product_id时，会自动关联已有的商品信息
    ## params
    - **plan_id**: 计划ID, 必选
    - **product_name**: 产品名称, str, 可选, 会根据该字段自动创建商品信息，当product_name和product同时存在时，以product指向的商品为准
    - **unit**: 规格, float, 可选
    - **amount**: 数量, int, 可选
    - **product_id**: 产品ID, int, 可选, 当product_name和product同时存在时，以product指向的商品为准
    - **order**: 订单编号或者订单编号, int | str, 必填
    - **order_field_type**: 排序字段类型, 可选

    ## 以下字段为保留字段, 保留字段可选
    - **operate_date**: 计划操作日期
    - **feeding_place**: 投料口转运
    - **feeding_warehouse**: 投料仓转运地点
    - **feeding**: 投料
    - **press**: 压榨
    - **refine**: 精炼
    - **sorting**: 分装
    - **warehousing**: 入库
    - **product_warehousing**: 成品入库地点
    - **notices**: 备注
    """
    try:
        with SessionLocal() as db:
            # 参数验证
            plan = db.query(Plan).filter(Plan.id == plan_id).first()
            if not plan:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "message": "计划不存在"},
                )

            # 验证订单
            if order_field_type == "id":
                order_obj = db.query(Order).filter(Order.id == order).first()
            else:
                order_obj = db.query(Order).filter(Order.order_number == order).first()
            if not order_obj:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "message": "订单不存在"},
                )

            # 验证产品
            if product_id:
                product = db.query(Product).filter(Product.id == product_id).first()
                if not product:
                    return JSONResponse(
                        status_code=status.HTTP_200_OK,
                        content={"code": 1, "message": "产品不存在"},
                    )
                product.amount += amount
            else:
                # 添加仓库信息
                product = Product(
                    name=product_name,
                    unit=unit,
                    amount=amount,
                )
            warehouse = Warehouse(
                amount=amount,
                operate_date=datetime.strptime(operate_date, "%Y-%m-%d %H:%M:%S")
                if operate_date
                else None,
                feeding_place=feeding_place,
                feeding_warehouse=feeding_warehouse,
                feeding=feeding,
                press=press,
                refine=refine,
                sorting=sorting,
                warehousing=warehousing,
                product_warehousing=product_warehousing,
                notices=notices,
            )
            warehouse.plan = plan
            warehouse.product = product
            warehouse.order = order_obj

            # 添加质检报告记录
            quality = Quality(
                name="质检报告",
                upload_time=datetime.now(),
                status="未上传",
                type="仓储加工",
            )
            quality.plan = plan
            warehouse.qualities.append(quality)

            db.add(warehouse)

            db.commit()

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 0, "message": "添加成功"},
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"添加仓库信息失败, {e}",
        )


@warehouse_router.put("/update_warehouse_status", summary="更新仓储加工状态信息")
async def update_warehouse_status(
    warehouse_id: int = Body(..., description="仓库ID"),
    warehouse_status: Literal["准备加工", "加工进行中", "加工完成"] = Body("准备加工", description="状态"),
):
    """
    # 更新仓库状态信息
    ## params
    - **warehouse_id**: 仓库ID
    - **warehouse_status**: 状态， 可选值：准备加工 | 加工进行中 | 加工完成
    """
    try:
        with SessionLocal() as db:
            warehouse = db.query(Warehouse).filter_by(id=warehouse_id).first()
            if not warehouse:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "message": "仓库不存在"},
                )
            warehouse.status = warehouse_status
            db.commit()
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 0, "message": "更新成功"},
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新仓库状态信息失败, {e}",
        )


@warehouse_router.put("/update_warehouse", summary="更新仓储加工信息")
async def update_warehouse(
    warehouse_id: int = Body(..., description="仓库ID"),
    amount: Optional[float] = Body(None, description="数量", examples=[100, 200]),
    product_id: Optional[int] = Body(None, description="产品ID"),
    order: Union[int, str, None] = Body(None, description="订单"),
    order_field_type: Literal["id", "num"] = Body("id", description="排序"),
    status: Optional[Literal["准备加工", "加工进行中", "加工完成"]] = Body(None, description="状态"),
):
    """
    # 更新仓库信息，product_name和product_id必须存在一个, 当填入product_name时，会自动创建商品信息,填入product_id时，会自动关联已有的商品信息
    ## params
    - **warehouse_id**: 仓库ID, 必选
    - **amount**: 数量, int, 可选
    - **product_id**: 产品ID, int, 可选
    - **order**: 订单编号或者订单编号, int | str, 可选
    - **order_field_type**: 排序字段类型, 可选
    - **status**: 状态, 可选, 可选值：准备加工 | 加工进行中 | 加工完成
    """
    try:
        with SessionLocal() as db:
            warehouse = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
            if not warehouse:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "message": "仓储加工环节不存在"},
                )

            # 验证订单
            if order:
                if order_field_type == "id":
                    order_obj = db.query(Order).filter(Order.id == order).first()
                else:
                    order_obj = (
                        db.query(Order).filter(Order.order_number == order).first()
                    )
                if not order_obj:
                    return JSONResponse(
                        status_code=status.HTTP_200_OK,
                        content={"code": 1, "message": "订单不存在"},
                    )
                warehouse.order = order_obj

            if product_id:
                product = db.query(Product).filter(Product.id == product_id).first()
                if not product:
                    return JSONResponse(
                        status_code=status.HTTP_200_OK,
                        content={"code": 1, "message": "产品不存在"},
                    )
                warehouse.product = product
            if amount:
                old_amount = warehouse.amount
                warehouse.amount = amount
                warehouse.product.amount = (
                    warehouse.product.amount - old_amount + amount
                )
            if status:
                warehouse.status = status
            db.commit()
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 0, "message": "更新成功"},
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新仓储加工信息失败, {e}",
        )


@warehouse_router.delete("/delete_warehouse", summary="删除仓库信息")
async def delete_warehouse(
    warehouse_id: int = Query(..., description="仓库ID"),
):
    """
    # 删除仓库信息
    ## params
    - **id**: 仓库ID
    """
    try:
        with SessionLocal() as db:
            warehouse = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
            if not warehouse:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "message": "仓储信息不存在"},
                )
            db.delete(warehouse)
            db.commit()
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 0, "message": "删除成功"},
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除仓储信息失败, {e}",
        )
