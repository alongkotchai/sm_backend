from fastapi import (
    APIRouter,
    HTTPException,
    status,
    Depends)
from utils import random_string
from uuid import uuid4, UUID
router = APIRouter(prefix='/models')


@router.get("")
def get_status():
    return {
        "name": "test",
        "version": "1.0a"
    }
