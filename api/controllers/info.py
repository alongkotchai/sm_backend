from fastapi import (
    APIRouter,
    HTTPException,
    status,
    Depends)
from schemas.info import InfoModel
router = APIRouter(prefix='/info')


@router.get("/status", response_model=InfoModel)
def get_status():
    return {
        "number_worker": 2,
        "task_queue_lenght": 5
    }
