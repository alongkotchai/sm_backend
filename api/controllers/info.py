from fastapi import (
    APIRouter,
    Depends)
from depends import (
    get_auth)
from schemas.info import InfoModel
from workers.manager import (
    get_status as status)

router = APIRouter(prefix='/info')


@router.get("/status", response_model=InfoModel)
def get_status(_=Depends(get_auth)):
    q, n = status()
    return {
        "number_worker": n,
        "task_queue_lenght": q
    }
