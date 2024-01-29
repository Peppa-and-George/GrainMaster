import sys
import time
import traceback
from datetime import timedelta

from fastapi import FastAPI, Response, Request, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from models.base import Token
from routers.user import router as user_router
from routers.product import product_router
from routers.plan import plan_router
from routers.location import location_router
from routers.client import client_router
from routers.privilege import privilege_router
from routers.transport import transport_router
from routers.warehouse import warehouse_router
from routers.logistics import logistics_router
from routers.order import order_router
from routers.camera import camera_router
from routers.plant import plant_router
from journal import log
from auth import (
    jwt,
    JWTError,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    SECRET_KEY,
    ALGORITHM,
    verify_password,
)
from config import IMAGE_DIR, VIDEOS_DIR
from schema.database import SessionLocal
from schema.tables import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="get_access_token")

app = FastAPI(title="backend", version="1.0.0")
app.include_router(
    user_router, tags=["系统管理"], dependencies=[Depends(oauth2_scheme)], prefix="/user"
)
app.mount("/image", StaticFiles(directory=IMAGE_DIR), name="image")
app.mount("/video", StaticFiles(directory=VIDEOS_DIR), name="video")
app.include_router(product_router, tags=["产品管理"], prefix="/product")
app.include_router(location_router, tags=["位置管理"], prefix="/location")
app.include_router(plan_router, tags=["计划管理"], prefix="/plan")
app.include_router(client_router, tags=["客户管理"], prefix="/client")
app.include_router(privilege_router, tags=["权益管理"], prefix="/privilege")
app.include_router(plant_router, tags=["田间种植管理"], prefix="/plant")
app.include_router(transport_router, tags=["运输管理"], prefix="/transport")
app.include_router(warehouse_router, tags=["仓储管理"], prefix="/warehouse")
app.include_router(logistics_router, tags=["物流计划"], prefix="/logistics")
app.include_router(order_router, tags=["订单管理"], prefix="/order")
app.include_router(camera_router, tags=["摄像头管理"], prefix="/camera")


async def sieve_middleware(request: Request, call_next):
    s_time = time.perf_counter()

    try:  # 为了防止fastapi因为奇怪的逻辑挂掉
        response = await call_next(request)
        e_time = time.perf_counter()
        c_time = e_time - s_time
        cost = "%.5fs" % c_time if c_time < 0 else "%.5fms" % (c_time * 1000)
        log.debug(
            f"{request.client.host}:{request.client.port} | {response.status_code} | {cost} | {request.method} | {request.url}"
        )
        return response
    except Exception:  # noqa
        e_time = time.perf_counter()
        c_time = e_time - s_time
        cost = "%.5fs" % c_time if c_time < 0 else "%.5fms" % (c_time * 1000)
        log.info(
            f"{request.client.host}:{request.client.port} | {500} | {cost} | {request.method} | {request.url}"
        )
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_tb(exc_traceback)
        log.error("\n" + exc_type.__name__ + " " + str(exc_value))
        return Response(f"{exc_type.__name__} {exc_value}", status_code=500)


app.middleware("http")(sieve_middleware)


async def get_current_user(token: str = Depends(oauth2_scheme)):  # 验证token
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    with SessionLocal() as db:
        user = db.query(User).filter(User.name == username).first()
        if not user:
            raise credentials_exception
        return user


@app.post("/get_access_token", response_model=Token, description="获取token", tags=["认证"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    with SessionLocal() as db:
        user = db.query(User).filter(User.name == form_data.username).first()
        if not verify_password(form_data.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.name}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}


def runserver(workers):
    import uvicorn

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8081,
        workers=workers,
        reload=True,
        # log_level="critical"
    )
