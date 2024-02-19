from fastapi import UploadFile
from pydantic import Field
from schemas.base import (
    InputModel,
    OutputModel,
    BaseList)


class ModelDisplay(OutputModel):
    name: str
    version: str


class ModelList(BaseList):
    models: list[ModelDisplay]


class ModelUpload(InputModel):
    name: str = Field(min_length=1,
                      max_length=32)
    version: str = Field('',
                         max_length=32)
    data1: UploadFile
    data2: UploadFile
    data3: UploadFile
