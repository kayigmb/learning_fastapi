import asyncio
import json
import re
from contextlib import asynccontextmanager
from functools import lru_cache
from typing import Annotated

import redis.asyncio as redis
from fastapi import Depends, FastAPI, Form, Request, Response, responses
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import Session
from sse_starlette.sse import EventSourceResponse
from starlette.status import HTTP_201_CREATED

from database import db, engine
from logger import logger
from models import Add, Base
from routes import login, webrtc
from utils.auth import RoleChecker, auth
from utils.config import settings
from utils.limitter import callback, identify
from utils.seeders import createRoleSeeds


@asynccontextmanager
@lru_cache(maxsize=200)
async def lifespan(app: FastAPI):
    logger.info("App Start")
    Base.metadata.create_all(engine)
    createRoleSeeds()
    redis_connection = redis.from_url(settings.REDIS_URL)
    await FastAPILimiter.init(
        redis=redis_connection,
        http_callback=callback,
        identifier=identify,
    )
    yield
    logger.info("App down")


app = FastAPI(title="API", version="1.01", lifespan=lifespan)


origins = [
    "http://localhost",
    "http://localhost:5173",
    "http://localhost:5174",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", dependencies=[Depends(RateLimiter(times=2, seconds=5))], tags=["Welcome"])
def main(user=Depends(auth)):
    return {"message": f"hello {user["name"].capitalize()}"}


app.include_router(router=login.router, prefix="/api/users")
app.include_router(router=webrtc.router, prefix="/api")


@app.middleware("http")
async def request_logging(request: Request, call_next):
    response = await call_next(request)
    print("request -------------", response)
    return response


async def serverEventGenerator(dab: AsyncSession = Depends(db)):
    try:
        while True:
            get_existing_user = select(Add)
            result = dab.execute(get_existing_user)
            total_names = result.scalars().all()
            display = [{"id": total.id, "name": total.name} for total in total_names]
            yield f"{json.dumps(display)}\n\n"
            await asyncio.sleep(10)
    except Exception as e:
        print(f"Error in event_generator: {str(e)}")
        yield f"data: {json.dumps({'error': str(e)})}\n\n"
        raise


@app.get("/names")
async def get_names(dab: db):
    try:
        return EventSourceResponse(serverEventGenerator(dab))

    except Exception as e:
        print(e)
        raise e


@app.post("/names")
def names(
    _: Annotated[bool, Depends(RoleChecker(allowedRoles=["superadmin", "buyer"]))],
    user=Depends(auth),
):
    try:
        return JSONResponse(
            content=f"New user has been added {user['email']}",
            status_code=HTTP_201_CREATED,
        )
    except Exception as e:
        print(e)


@app.post("/webhook", dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def webhook(request: Request):
    print(await request.json())
    return JSONResponse(content={"message": "nice"}, status_code=201)
