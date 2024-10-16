import uuid
from datetime import datetime
from enum import unique

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(50), unique=True)
    password: Mapped[str] = mapped_column(String(500))
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    role: Mapped[str] = mapped_column(
        String[50], ForeignKey("roles.id", onupdate="CASCADE", ondelete="SET NULL")
    )
    createdAt: Mapped[DateTime] = mapped_column(
        DateTime, default=lambda: datetime.now()
    )

    def __repr__(self) -> str:
        return (
            f"id: {self.id} id:{self.name} email: {self.email} verified:{self.verified}"
        )


class Roles(Base):
    __tablename__ = "roles"
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(50), unique=True)

    def __repr__(self) -> str:
        return f"id: {self.id} name:{self.name} "


class Room(Base):
    __tablename__ = "rooms"
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    roomName: Mapped[str] = mapped_column(String(100))
    room1Name: Mapped[str] = mapped_column(String(100))
    roomConnection: Mapped[str] = mapped_column(String(10000))

    def __repr__(self) -> str:
        return f"id: {self.id} name: {self.roomName}"


class Add(Base):
    __tablename__ = "add"
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(30))

    def __repr__(self) -> str:
        return f"id: {self.id} name: {self.name}"
