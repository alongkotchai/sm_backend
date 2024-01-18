import uuid
from typing import Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy import (
    text)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column)
from sqlalchemy.dialects.mysql import (
    TIMESTAMP,
    VARCHAR,
    BOOLEAN)
from core.security import Role


class Base(AsyncAttrs, DeclarativeBase):
    """
    Base orm class for sqlalchemy orm
    """

    def __str__(self) -> str:
        """generate string represent ORM object

        Returns:
            str:
        """
        return self.__class__.__name__+'(' + ', '.join(
            k + '=' + str(self.__dict__[k])
            for k in sorted(self.__dict__.keys())
            if k != '_sa_instance_state') + ')'


class User(Base):
    """
        Class represent the users tables orm
    """

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        VARCHAR(36),
        primary_key=True)
    email: Mapped[str] = mapped_column(
        VARCHAR(64),
        nullable=False,
        unique=True,
        index=True)
    password: Mapped[str] = mapped_column(
        VARCHAR(64),
        nullable=False)
    last_login: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(),
        default=None,
        nullable=True)
    create_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(),
        default=datetime.utcnow())
    role: Mapped[Role] = mapped_column(
        VARCHAR(8),
        nullable=False,
        default=Role.USER)
    is_activate: Mapped[bool] = mapped_column(
        BOOLEAN(),
        nullable=False,
        default=False)
