from fastapi import APIRouter
from sqlalchemy import func
from schema.tables import Client, Order
from schema.database import SessionLocal

client_router = APIRouter()


@client_router.get("/statistic_clients_info", summary="统计客户信息")
async def statistic_clients_info_api():
    """
    # 统计客户信息
    """
    with SessionLocal() as db:
        res = db.query(Client.type, func.count(Client.id)).group_by(Client.type).all()
        total = db.query(func.count(Client.id)).scalar()
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


@client_router.get("/statistic_order_info", summary="统计客户信息")
async def statistic_order_info_api():
    """
    # 统计客户信息
    """
    with SessionLocal() as db:
        res = db.query(Order.type, func.count(Order.id)).group_by(Order.status).all()
        total = db.query(func.count(Client.id)).scalar()
        data = [
            {
                "type": item[0],
                "count": item[1],
            }
            for item in res
        ]
        return {
            "code": 0,
            "message": "success",
            "data": {
                "total": total,
                "detail": data,
            },
        }
