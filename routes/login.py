from typing import Annotated

from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import defer
from starlette.status import (
    HTTP_201_CREATED,
    HTTP_401_UNAUTHORIZED,
    HTTP_406_NOT_ACCEPTABLE,
)

from database import db
from logger import logger
from models import Roles, User
from typeModels import GetUser, LoginType
from utils.auth import create_access_token
from utils.encrypt import PasswordEncrypt

router = APIRouter(tags=["Authentication"])


@router.post("/signup", status_code=HTTP_201_CREATED)
async def Signup(database: db, data: Annotated[GetUser, Form()]):
    try:
        getExistingUser = select(User).where(data.email == User.email)
        getExistingRole = select(Roles).where("buyer" == Roles.name)

        result = database.execute(getExistingUser)
        resultRole = database.execute(getExistingRole)

        isUserExist = result.scalars().first()
        isRoleExist = resultRole.scalars().first()

        if not isRoleExist:
            return HTTPException(
                status_code=404,
                detail="Invalid Role",
            )

        if isUserExist:
            return HTTPException(
                status_code=HTTP_406_NOT_ACCEPTABLE,
                detail="Email already exists",
            )

        hashPassword = PasswordEncrypt.hash(data.password)
        saveNewUser = User(
            name=data.name, email=data.email, password=hashPassword, role=isRoleExist.id
        )

        database.add(saveNewUser)
        database.commit()

        return {
            "message": "User successfully signed up",
            "user": {data.email, data.name},
        }
    except Exception as e:
        print(e)
        return JSONResponse(content=f"Error happened {e}", status_code=500)


@router.post("/login", status_code=201)
async def Login(dab: db, data: Annotated[LoginType, Form()]):
    try:
        query = dab.execute(select(User).where(data.email == User.email))
        isUserExist = query.scalars().first()
        if not isUserExist:
            logger.info("Invalid Email or password")
            return HTTPException(
                status_code=HTTP_401_UNAUTHORIZED, detail="Invalid Email or Password"
            )

        checkPassword = PasswordEncrypt.verify(data.password, isUserExist.password)
        if not checkPassword:
            return HTTPException(
                status_code=HTTP_401_UNAUTHORIZED, detail="Invalid Email or Password"
            )

        userData = {
            "name": isUserExist.name,
            "email": isUserExist.email,
            "role": isUserExist.role,
        }
        accessToken = create_access_token(data=userData)

        return {"access_token": accessToken, "token_type": "bearer"}
    except Exception as e:
        logger.error("Invalid Email or Password, Error with the login")
        print(e)
        return JSONResponse(content=f"Error happened {e}", status_code=500)


@router.get("/", status_code=200)
async def getUsers(database: db):
    try:
        query = database.execute(select(User).options(defer(User.password)))
        getAllUsers = query.scalars().all()
        if not getAllUsers:
            return JSONResponse(content="Error happened: NO users", status_code=404)
        return getAllUsers
    except Exception as e:
        print(e)
        return JSONResponse(content=f"Error happened {e}", status_code=500)
