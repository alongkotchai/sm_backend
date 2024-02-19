import uuid
from typing import (
    Any,
    Optional,
    Iterable)
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy import (
    desc,
    ForeignKey,
    String)
from sqlalchemy.orm import (
    InstrumentedAttribute,
    DeclarativeBase,
    Mapped,
    mapped_column)
from sqlalchemy.dialects.mysql import (
    LONGBLOB,
    INTEGER,
    TIMESTAMP,
    VARCHAR,
    DATETIME,
    BOOLEAN,
    FLOAT,
    TEXT)
from core.security import Role
from schemas.base import (
    TaskType,
    TaskStatus)


class Base(AsyncAttrs, DeclarativeBase):
    """
    Base orm class for sqlalchemy orm
    """

    searchable: set[str]
    orderable: set[str]

    @classmethod
    def _order(cls, attr: Iterable[str], is_desc: bool = False):

        used = set()

        def _select_stmt(key: str):
            used.add(key)
            return (cls._acol(key) if not is_desc
                    else desc(cls._acol(key)))

        return (_select_stmt(key) for key in attr
                if key in cls.orderable and key not in used)

    @classmethod
    def _like(cls, attr: Optional[dict[str, Any]] = None):
        if not attr:
            return tuple()

        def _select_stmt(col: InstrumentedAttribute, value: Any):
            if isinstance(col.type, String):
                return (col.contains(value, autoescape=True))
            return (col == value)

        return (_select_stmt(cls._acol(key), attr[key])
                for key in attr
                if key in cls.searchable)

    @classmethod
    def _acol(cls, __name: str) -> InstrumentedAttribute:
        if __name not in cls.__table__.columns:
            raise KeyError(f'no column with name: {__name}')
        return cls.__getattribute__(cls, __name)

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

    uid: Mapped[uuid.UUID] = mapped_column(
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
    is_active: Mapped[bool] = mapped_column(
        BOOLEAN(),
        nullable=False,
        default=False)


class Model(Base):
    """
        Class represent the models tables orm
    """

    __tablename__ = "models"

    name: Mapped[str] = mapped_column(
        VARCHAR(32),
        primary_key=True)
    version: Mapped[str] = mapped_column(
        VARCHAR(32),
        nullable=False,
        default='')
    data1: Mapped[bytes] = mapped_column(
        LONGBLOB(),
        nullable=False)
    data2: Mapped[bytes] = mapped_column(
        LONGBLOB(),
        nullable=False)
    data3: Mapped[bytes] = mapped_column(
        LONGBLOB(),
        nullable=False)


class Tasks(Base):
    """
        Class represent the tasks tables orm
    """

    __tablename__ = "tasks"

    tid: Mapped[uuid.UUID] = mapped_column(
        VARCHAR(36),
        primary_key=True)
    name: Mapped[str] = mapped_column(
        VARCHAR(32),
        nullable=False,
        unique=True,
        index=True)
    uid: Mapped[uuid.UUID] = mapped_column(
        VARCHAR(36),
        ForeignKey('users.uid', ondelete='SET NULL'),
        nullable=True)
    m_name: Mapped[str] = mapped_column(
        VARCHAR(32),
        ForeignKey('models.name', ondelete='SET NULL'),
        nullable=True)
    create_at: Mapped[datetime] = mapped_column(
        DATETIME(),
        nullable=False)
    start_time: Mapped[datetime] = mapped_column(
        DATETIME(),
        nullable=True)
    finish_time: Mapped[datetime] = mapped_column(
        DATETIME(),
        nullable=True)
    task_type: Mapped[TaskType] = mapped_column(
        VARCHAR(8),
        nullable=False)
    status: Mapped[TaskStatus] = mapped_column(
        VARCHAR(8),
        nullable=False)


class Output(Base):
    """
        Class represent the outputs tables orm
    """

    __tablename__ = "outputs"

    tid: Mapped[uuid.UUID] = mapped_column(
        VARCHAR(36),
        ForeignKey('tasks.tid', ondelete='CASCADE'),
        primary_key=True)
    index: Mapped[int] = mapped_column(
        INTEGER(),
        primary_key=True)
    file_ref: Mapped[str] = mapped_column(
        VARCHAR(128),
        nullable=False)
    p1_x: Mapped[float] = mapped_column(
        FLOAT(),
        nullable=True,
        default=None)
    p1_y: Mapped[float] = mapped_column(
        FLOAT(),
        nullable=True,
        default=None)
    p1_h: Mapped[float] = mapped_column(
        FLOAT(),
        nullable=True,
        default=None)
    p1_w: Mapped[float] = mapped_column(
        FLOAT(),
        nullable=True,
        default=None)
    p1_predict: Mapped[float] = mapped_column(
        FLOAT(),
        nullable=True,
        default=None)
    p2_x: Mapped[float] = mapped_column(
        FLOAT(),
        nullable=True,
        default=None)
    p2_y: Mapped[float] = mapped_column(
        FLOAT(),
        nullable=True,
        default=None)
    p2_h: Mapped[float] = mapped_column(
        FLOAT(),
        nullable=True,
        default=None)
    p2_w: Mapped[float] = mapped_column(
        FLOAT(),
        nullable=True,
        default=None)
    p2_predict: Mapped[float] = mapped_column(
        FLOAT(),
        nullable=True,
        default=None)


class Input(Base):
    """
        Class represent the inputs tables orm
    """

    __tablename__ = "inputs"

    tid: Mapped[uuid.UUID] = mapped_column(
        VARCHAR(36),
        ForeignKey('tasks.tid', ondelete='CASCADE'),
        primary_key=True)

    index: Mapped[int] = mapped_column(
        INTEGER(),
        primary_key=True)

    source_ref: Mapped[str] = mapped_column(
        TEXT(),
        nullable=False)
