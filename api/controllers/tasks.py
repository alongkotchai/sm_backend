from fastapi import (
    APIRouter,
    HTTPException,
    status,
    Depends)

from utils import random_string
from uuid import uuid4, UUID
router = APIRouter(prefix='/tasks')


@router.get("")
def get_tasks():
    return {
        "tasks": [
            {"id": uuid4(),
             "name": "T1",
             "user_id": uuid4(),
             "number_input": 20,
             "processed": 20,
             "start_time": "2024-01-26T23:30:11",
             "finish_time": "2024-01-26T23:32:11",
             "task_type": "batch",
             "status": "finish",
             "input_list": [
                 random_string(5) + ".png" for i in range(20)
            ]},
            {"id": uuid4(),
             "name": "T2",
             "user_id": uuid4(),
             "number_input": 33,
             "processed": 10,
             "start_time": "2024-01-26T23:30:11",
             "finish_time": None,
             "task_type": "batch",
             "status": "running",
             "input_list": [
                 random_string(5) + ".png" for i in range(33)
            ]},
            {"id": uuid4(),
             "name": "T3",
             "user_id": uuid4(),
             "number_input": 16,
             "processed": 0,
             "start_time": "2024-01-26T23:30:11",
             "finish_time": None,
             "task_type": "batch",
             "status": "wating",
             "input_list": [
                 random_string(5) + ".png" for i in range(16)
            ]},
            {"id": UUID(int=1231231),
             "name": "T4",
             "user_id": uuid4(),
             "number_input": 1,
             "processed": 0,
             "start_time": None,
             "finish_time": None,
             "task_type": "batch",
             "status": "created",
             "input_list": [
                 "abcde.png"
            ]}
        ]
    }


@router.get("/{id}")
def get_one_tasks(id: UUID):
    return {
        "id": id,
        "name": "T99",
        "user_id": uuid4(),
        "number_input": 1,
        "processed": 0,
        "start_time": None,
        "finish_time": None,
        "task_type": "batch",
        "status": "created",
        "input_list": [
            "abcde.png"
        ]
    }


@router.post("")
def post_tasks():
    return {"id": uuid4(),
            "name": "T7",
            "user_id": uuid4(),
            "number_input": 3,
            "processed": 0,
            "start_time": None,
            "finish_time": None,
            "task_type": "batch",
            "status": "create",
            "input_list": [
        "abcde.png",
        "abcdf.png",
        "abcdg.png",
    ]}


@router.delete("/{id}")
def delete_tasks(id: UUID):
    return {
        "success": True
    }


@router.put("/{id}")
def put_tasks(id: UUID):
    return {
        "id": id,
        "name": "T7",
        "user_id": uuid4(),
        "number_input": 5,
        "processed": 0,
        "start_time": None,
        "finish_time": None,
        "task_type": "batch",
        "status": "create",
        "input_list": [
            "abcde.png",
            "abcdf.png",
            "abcdg.png",
        ] + [
            random_string(5) + ".png" for i in range(2)
        ]
    }


@router.post("/{id}/start")
def start_task(id: UUID):
    return {
        "success": True
    }


@router.post("/{id}/stop")
def start_task(id: UUID):
    return {
        "success": True
    }
