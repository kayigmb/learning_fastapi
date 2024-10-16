import re
from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel, field_validator, model_validator
from starlette.status import HTTP_404_NOT_FOUND, HTTP_417_EXPECTATION_FAILED
from starlette.types import HTTPExceptionHandler


class GetUser(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    confirmPassword: Optional[str] = None

    @field_validator("name")
    def validateName(cls, v):
        if not v:
            raise HTTPException(detail="Name is required", status_code=404)
        return v

    @field_validator("email")
    def validatingEmail(cls, v):
        if not v:
            raise HTTPException(detail="Email is required", status_code=404)
        if not re.match(r"^[a-z\d]+@[a-z\d]+\.(com|net|rw|org)$", v):
            raise HTTPException(detail="Enter a valid Email", status_code=400)

        return v

    @field_validator("password")
    def validatingPassword(cls, v):
        if not v:
            raise HTTPException(detail="Password is required", status_code=404)
        if not re.match(
            r"^(?=.*[a-zA-Z])(?=.*\d)[A-Za-z\d!@#$&]{6,15}$",
            v,
        ):
            raise HTTPException(
                detail="Password should have more than 6-15 characters, a capital letter, and a symbol",
                status_code=400,
            )
        return v

    @model_validator(mode="after")
    def validateConfirmPassword(self):
        if self.confirmPassword != self.password:
            raise HTTPException(
                detail="Passwords are not matching",
                status_code=HTTP_417_EXPECTATION_FAILED,
            )
        return self


class AddName(BaseModel):
    name: Optional[str] = None

    @field_validator("name")
    def validatingEmail(cls, v):
        if not v:
            raise HTTPException(detail="Names is required", status_code=404)
        return v


class RoomItems(BaseModel):
    roomName: str
    channelConnection: Optional[str] = None

    @field_validator("roomName")
    async def ValidateRoom(cls, v):
        if not v:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail="Room \
                                Name is required",
            )
        return v


class LoginType(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None

    @field_validator("email")
    def validateEmail(cls, v):
        if not v:
            return HTTPException(detail="Email is required", status=404)
        return v

    @field_validator("password")
    def validatePassword(cls, v):
        if not v:
            return HTTPException(detail="Password is required", status_code=404)
        return v
