import sys
import time
import traceback
from datetime import timedelta

from fastapi import FastAPI, Response, Request, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from routers.user import router as user_router
from models.base import Token
from schema.curd import CURD

from journal import log
from auth import jwt, JWTError, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="get_access_token")
curd = CURD()

app = FastAPI(title="backend", version="1.0.0")
app.include_router(user_router, tags=["系统管理"], dependencies=[Depends(oauth2_scheme)], prefix="/user")


async def sieve_middleware(request: Request, call_next):
    s_time = time.perf_counter()

    try:    # 为了防止fastapi因为奇怪的逻辑挂掉
        response = await call_next(request)
        e_time = time.perf_counter()
        c_time = e_time - s_time
        cost = "%.5fs" % c_time if c_time < 0 else "%.5fms" % (c_time * 1000)
        log.debug(f"{request.client.host}:{request.client.port} | {response.status_code} | {cost} | {request.method} | {request.url}")
        return response
    except Exception:   # noqa
        e_time = time.perf_counter()
        c_time = e_time - s_time
        cost = "%.5fs" % c_time if c_time < 0 else "%.5fms" % (c_time * 1000)
        log.info(f"{request.client.host}:{request.client.port} | {500} | {cost} | {request.method} | {request.url}")
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_tb(exc_traceback)
        log.error("\n" + exc_type.__name__ + " " + str(exc_value))
        return Response(f"{exc_type.__name__} {exc_value}", status_code=500)


app.middleware('http')(sieve_middleware)


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
    user = curd.user.get_user(username)
    if user is None:
        raise credentials_exception
    return user


@app.post("/get_access_token", response_model=Token, description="获取token", tags=["认证"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = curd.user.check_user(form_data.username, form_data.password)
    if not user:
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
        "app:app", host="0.0.0.0", port=10001, workers=workers, reload=True,
        # log_level="critical"
    )
