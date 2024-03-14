from fastapi import (
    APIRouter,
    Depends)
from depends import (
    get_auth)
from schemas.info import InfoModel
from workers.manager import (
    get_status as status,
    get_rt_status as rt_status)

router = APIRouter(prefix='/info')


@router.get("/status", response_model=InfoModel)
def get_status(_=Depends(get_auth)):
    q, n = status()
    return {
        "number_worker": n,
        "task_queue_lenght": q
    }


@router.get("/rt_status")
def get_rt_status(_=Depends(get_auth)):
    return rt_status()
