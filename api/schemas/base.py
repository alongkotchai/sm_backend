from math import ceil
from typing import (
    Any)
from enum import Enum
from fastapi import Query
from pydantic import (
    BaseModel,
    ConfigDict)


class TaskType(str, Enum):
    BATCH = 'batch'
    VIDEO = 'video'
    CAMERA = 'camera'


class TaskStatus(str, Enum):
    CREATE = 'created',
    WAIT = 'waiting'
    RUN = 'running',
    FINISH = 'finished'


class InputModel(BaseModel):

    model_config = ConfigDict(
        str_strip_whitespace=True)


class OutputModel(BaseModel):

    model_config = ConfigDict(
        from_attributes=True)


class BaseList(OutputModel):
    page_number: int
    page_size: int
    last_page: int
    count: int


class ConfirmRes(OutputModel):
    success: bool


def last_page(total: int, size: int) -> int:
    return ceil(float(total) / size)


class QueryBase(InputModel):

    page: int = Query(1, ge=1)
    size: int = Query(25, ge=1, lt=100)
    desc: bool = Query(False)

    def to_search_dict(self) -> dict[str, Any]:
        return self.model_dump(exclude_none=True,
                               exclude=['page', 'size', 'desc'])
