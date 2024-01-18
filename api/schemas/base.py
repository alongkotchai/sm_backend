from pydantic import (
    BaseModel,
    ConfigDict)


class BaseList(BaseModel):
    page_number: int
    page_size: int
    last_page: int
    count: int

    model_config = ConfigDict(
        from_attributes=True)
