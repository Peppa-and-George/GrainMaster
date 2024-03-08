from fastapi import APIRouter
from sqlalchemy import func
from schema.tables import (
    Client,
    PlantPlan,
    Warehouse,
    Transport,
    LogisticsPlan,
    Camera,
    Location,
    Order,
    Plan,
)
from schema.database import SessionLocal

statistic_router = APIRouter()


@statistic_router.get("/statistic_clients_info", summary="统计客户信息")
async def statistic_clients_info_api():
    """
    # 统计客户信息
    """
    with SessionLocal() as db:
        res = db.query(Client.type, func.count(Client.id)).group_by(Client.type).all()
        total = db.query(func.count(Client.id)).scalar()
        if total == 0:
            return {
                "code": 0,
                "message": "success",
                "data": {
                    "total": 0,
                    "detail": "无数据",
                },
            }
        data = [
            {
                "type": item[0],
                "count": item[1],
                "proportion": int((item[1] / total) * 100),
            }
            for item in res
        ]
        total_proportion = sum([item["proportion"] for item in data])
        data[-1]["proportion"] += 100 - total_proportion
        return {
            "code": 0,
            "message": "success",
            "data": {
                "total": total,
                "detail": data,
            },
        }


@statistic_router.get("/statistic_plan_info", summary="统计计划信息")
async def statistic_plan_info_api():
    """
    # 统计计划信息
    """
    with SessionLocal() as db:
        plant_total = db.query(func.count(PlantPlan.plan_id)).scalar()
        warehouse_total = db.query(func.count(Warehouse.id)).scalar()
        transport_total = db.query(func.count(Transport.id)).scalar()
        Logistics_total = db.query(func.count(LogisticsPlan.id)).scalar()
        return {
            "code": 0,
            "message": "success",
            "data": {
                "田间种植": plant_total,
                "仓储加工": warehouse_total,
                "原料运输": transport_total,
                "物流运输": Logistics_total,
            },
        }


@statistic_router.get("/statistic_camera_info", summary="统计摄像头信息")
async def statistic_camera_info_api():
    """
    # 统计摄像头信息
    """
    with SessionLocal() as db:
        total = db.query(func.count(Camera.id)).scalar()
        return {
            "code": 0,
            "message": "success",
            "data": {
                "total": total,
            },
        }


@statistic_router.get("/get_location_info", summary="获取位置信息")
async def get_location_info_api():
    """
    # 获取位置信息
    """
    with SessionLocal() as db:
        res = db.query(Location).all()
        data = [
            {
                "name": item.name,
                "type": item.type,
                "longitude": item.longitude,
                "latitude": item.latitude,
                "customized": item.customized,
                "area": item.area,
            }
            for item in res
        ]
        return {
            "code": 0,
            "message": "success",
            "data": data,
        }


@statistic_router.get("/get_order_info", summary="获取订单汇总信息")
async def get_order_info_api():
    """
    # 获取订单汇总信息
    """
    with SessionLocal() as db:
        query = db.query(Order.status, func.count(Order.id)).group_by(Order.status)
        data = [
            {
                "status": item[0],
                "count": item[1],
            }
            for item in query.all()
        ]
        total = sum([item["count"] for item in data])
        return {
            "code": 0,
            "message": "success",
            "data": {
                "total": total,
                "detail": data,
            },
        }


@statistic_router.get("/get_material_info", summary="获取原料和成品汇总信息")
async def get_material_info_api():
    """
    # 获取原料和成品汇总信息
    """
    with SessionLocal() as db:
        plans = db.query(Plan).all()
        total_material = 0.0
        total_product = 0.0
        for plan in plans:
            total_material += plan.total_material if plan.total_material else 0
            total_product += plan.total_product if plan.total_product else 0
        return {
            "code": 0,
            "message": "success",
            "data": {
                "total_material": total_material,
                "total_product": total_product,
            },
        }
