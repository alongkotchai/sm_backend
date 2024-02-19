from schemas.base import OutputModel


class InfoModel(OutputModel):
    number_worker: int
    task_queue_lenght: int
