from fastapi import (
    APIRouter,
    HTTPException,
    status,
    Depends)

router = APIRouter(prefix='/info')


@router.get("/status")
def get_status():
    return {
        "number_worker": 2,
        "task_queue_lenght": 5
    }
