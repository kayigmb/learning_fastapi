from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Boolean, select

from database import db
from logger import logger
from models import Roles
from utils.config import settings

authenticationScheme = HTTPBearer()

ALGORITHM = settings.ALGORITHM
SECRET_KEY = settings.SECRET_KEY
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


def create_access_token(data: dict):
    to_encode = data.copy()
    expires_delta = timedelta(minutes=float(ACCESS_TOKEN_EXPIRE_MINUTES))
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=10)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def auth(
    credentials: HTTPAuthorizationCredentials = Depends(authenticationScheme),
):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        logger.info("Credential Error")

        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No payload Found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload
    except Exception as e:
        logger.info("Error in authorization")
        print(e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Error validation token: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )


class RoleChecker:
    def __init__(self, allowedRoles: list[str]) -> None:
        self.allowedRoles = allowedRoles

    async def __call__(self, database: db, user=Depends(auth)) -> Boolean:
        allowed = []

        for role in self.allowedRoles:
            query = database.execute(select(Roles).where(role == Roles.name))
            queryResult = query.scalars().first()
            allowed.append(queryResult.id)

        if user["role"] not in allowed:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized access",
            )
        return True
