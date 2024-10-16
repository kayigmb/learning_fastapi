from math import ceil

from fastapi import HTTPException, Request, Response
from starlette.status import HTTP_429_TOO_MANY_REQUESTS

from logger import logger


async def identify(request: Request):
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        logger.info("Too many request from {}".format(forwarded))
        return forwarded.split(",")[0]
    logger.info(
        "Too many request from {}:{}".format(request.client, request.scope["path"])
    )
    return


async def callback(request: Request, response: Response, pexpire: int):
    expire = ceil(pexpire / 1000)
    raise HTTPException(
        HTTP_429_TOO_MANY_REQUESTS,
        "Too Many Requests",
        headers={"Retry-After": str(expire)},
    )
