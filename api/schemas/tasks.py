from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import (
    Field,
    BaseModel,
    ConfigDict,
    field_validator)
from core.security import Role
from schemas.base import (
    TaskStatus,
    TaskType,
    InputModel,
    OutputModel,
    BaseList)


class InputDisplay(OutputModel):
    index: int
    source_ref: str


class TaskDisplay(OutputModel):
    tid: UUID
    name: str
    uid: UUID
    m_name: str
    create_at: datetime
    start_time: Optional[datetime]
    finish_time: Optional[datetime]
    task_type: TaskType
    status: TaskStatus
    number_of_input: int = 0
    processed: int = 0
    input_list: list[InputDisplay] = []


class TaskList(BaseList):
    tasks: list[TaskDisplay]


class TaskCreate(InputModel):
    name: str = Field(min_length=1,
                      max_length=32)
    m_name: str = Field('default',
                        min_length=1,
                        max_length=32)
    task_type: TaskType = Field(TaskType.BATCH)
    input_list: list[str] = []


class TaskModify(InputModel):
    name: Optional[str] = Field(None,
                                min_length=1,
                                max_length=32)
    m_name: Optional[str] = Field(None,
                                  min_length=1,
                                  max_length=32)

    input_to_remove: list[int] = Field([])
    input_to_add: list[str] = Field([])
