from uuid import UUID
from datetime import datetime
from typing import Optional
from schemas.base import (
    TaskStatus,
    TaskType,
    OutputModel,
    BaseList)


class PointDisplay(OutputModel):
    center_x: Optional[float] = None
    center_y: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    predict: Optional[float] = None


class ResultOutput(OutputModel):
    p1: PointDisplay
    p2: PointDisplay
    input_file: str
    output_file: str


class ResultSum(OutputModel):
    tid: UUID
    outputs: list[ResultOutput] = []


class ResultDetail(ResultSum):
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


class ResultList(BaseList):
    results: list[ResultSum] = []
