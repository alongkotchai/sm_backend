from fastapi import (
    APIRouter,
    HTTPException,
    status,
    Depends)

from uuid import uuid4, UUID
router = APIRouter(prefix='/results')


@router.get("/summary")
def get_summary():
    return {
        "results": [
            {
                "task_id": uuid4(),
                "outputs": [
                    {
                        "p1": {
                            "center_x": 99.0,
                            "center_y": 99.0,
                            "width": 10.0,
                            "height": 10.0,
                            "predict": 9.99
                        },
                        "p2": {
                            "center_x": 99.0,
                            "center_y": 99.0,
                            "width": 10.0,
                            "height": 10.0,
                            "predict": 9.99
                        },
                        "input_file": "abcde.png",
                        "output_file": "cdefg.png"
                    },
                    {
                        "p1": {
                            "center_x": 99.0,
                            "center_y": 99.0,
                            "width": 10.0,
                            "height": 10.0,
                            "predict": 9.99
                        },
                        "p2": {
                            "center_x": 99.0,
                            "center_y": 99.0,
                            "width": 10.0,
                            "height": 10.0,
                            "predict": 9.99
                        },
                        "input_file": "abcdf.png",
                        "output_file": "cdefh.png"
                    },
                    {
                        "p1": {
                            "center_x": 99.0,
                            "center_y": 99.0,
                            "width": 10.0,
                            "height": 10.0,
                            "predict": 9.99
                        },
                        "p2": {
                            "center_x": 99.0,
                            "center_y": 99.0,
                            "width": 10.0,
                            "height": 10.0,
                            "predict": 9.99
                        },
                        "input_file": "abcdg.png",
                        "output_file": "cdefi.png"
                    },
                    {
                        "p1": {
                            "center_x": 99.0,
                            "center_y": 99.0,
                            "width": 10.0,
                            "height": 10.0,
                            "predict": 9.99
                        },
                        "p2": {
                            "center_x": 99.0,
                            "center_y": 99.0,
                            "width": 10.0,
                            "height": 10.0,
                            "predict": 9.99
                        },
                        "input_file": "abcdh.png",
                        "output_file": "cdefj.png"
                    }
                ]
            },
            {
                "task_id": uuid4(),
                "outputs": [
                    {
                        "p1": {
                            "center_x": 99.0,
                            "center_y": 99.0,
                            "width": 10.0,
                            "height": 10.0,
                            "predict": 9.99
                        },
                        "p2": {
                            "center_x": 99.0,
                            "center_y": 99.0,
                            "width": 10.0,
                            "height": 10.0,
                            "predict": 9.99
                        },
                        "input_file": "abcde.png",
                        "output_file": "cdefg.png"
                    },
                    {
                        "p1": {
                            "center_x": 99.0,
                            "center_y": 99.0,
                            "width": 10.0,
                            "height": 10.0,
                            "predict": 9.99
                        },
                        "p2": {
                            "center_x": 99.0,
                            "center_y": 99.0,
                            "width": 10.0,
                            "height": 10.0,
                            "predict": 9.99
                        },
                        "input_file": "abcdf.png",
                        "output_file": "cdefh.png"
                    },
                    {
                        "p1": {
                            "center_x": 99.0,
                            "center_y": 99.0,
                            "width": 10.0,
                            "height": 10.0,
                            "predict": 9.99
                        },
                        "p2": {
                            "center_x": 99.0,
                            "center_y": 99.0,
                            "width": 10.0,
                            "height": 10.0,
                            "predict": 9.99
                        },
                        "input_file": "abcdg.png",
                        "output_file": "cdefi.png"
                    },
                    {
                        "p1": {
                            "center_x": 99.0,
                            "center_y": 99.0,
                            "width": 10.0,
                            "height": 10.0,
                            "predict": 9.99
                        },
                        "p2": {
                            "center_x": 99.0,
                            "center_y": 99.0,
                            "width": 10.0,
                            "height": 10.0,
                            "predict": 9.99
                        },
                        "input_file": "abcdh.png",
                        "output_file": "cdefj.png"
                    },
                    {
                        "p1": {
                            "center_x": 99.0,
                            "center_y": 99.0,
                            "width": 10.0,
                            "height": 10.0,
                            "predict": 9.99
                        },
                        "p2": {
                            "center_x": 99.0,
                            "center_y": 99.0,
                            "width": 10.0,
                            "height": 10.0,
                            "predict": 9.99
                        },
                        "input_file": "abcde.png",
                        "output_file": "cdefg.png"
                    },
                    {
                        "p1": {
                            "center_x": 99.0,
                            "center_y": 99.0,
                            "width": 10.0,
                            "height": 10.0,
                            "predict": 9.99
                        },
                        "p2": {
                            "center_x": 99.0,
                            "center_y": 99.0,
                            "width": 10.0,
                            "height": 10.0,
                            "predict": 9.99
                        },
                        "input_file": "abcdf.png",
                        "output_file": "cdefh.png"
                    },
                    {
                        "p1": {
                            "center_x": 99.0,
                            "center_y": 99.0,
                            "width": 10.0,
                            "height": 10.0,
                            "predict": 9.99
                        },
                        "p2": {
                            "center_x": 99.0,
                            "center_y": 99.0,
                            "width": 10.0,
                            "height": 10.0,
                            "predict": 9.99
                        },
                        "input_file": "abcdg.png",
                        "output_file": "cdefi.png"
                    },
                    {
                        "p1": {
                            "center_x": 99.0,
                            "center_y": 99.0,
                            "width": 10.0,
                            "height": 10.0,
                            "predict": 9.99
                        },
                        "p2": {
                            "center_x": 99.0,
                            "center_y": 99.0,
                            "width": 10.0,
                            "height": 10.0,
                            "predict": 9.99
                        },
                        "input_file": "abcdh.png",
                        "output_file": "cdefj.png"
                    }
                ]
            }
        ]
    }


@router.get("/{id}")
def get_detail(id: UUID):
    return {
        "task_id": id,
        "name": "T99",
        "user_id": uuid4(),
        "number_input": 4,
        "processed": 4,
        "start_time": "2024-01-26T23:30:11",
        "finish_time": "2024-01-26T23:31:11",
        "task_type": "batch",
        "status": "finish",
        "outputs": [
            {
                "p1": {
                    "center_x": 99.0,
                    "center_y": 99.0,
                    "width": 10.0,
                    "height": 10.0,
                    "predict": 9.99
                },
                "p2": {
                    "center_x": 99.0,
                    "center_y": 99.0,
                    "width": 10.0,
                    "height": 10.0,
                    "predict": 9.99
                },
                "input_file": "abcde.png",
                "output_file": "cdefg.png"
            },
            {
                "p1": {
                    "center_x": 99.0,
                    "center_y": 99.0,
                    "width": 10.0,
                    "height": 10.0,
                    "predict": 9.99
                },
                "p2": {
                    "center_x": 99.0,
                    "center_y": 99.0,
                    "width": 10.0,
                    "height": 10.0,
                    "predict": 9.99
                },
                "input_file": "abcdf.png",
                "output_file": "cdefh.png"
            },
            {
                "p1": {
                    "center_x": 99.0,
                    "center_y": 99.0,
                    "width": 10.0,
                    "height": 10.0,
                    "predict": 9.99
                },
                "p2": {
                    "center_x": 99.0,
                    "center_y": 99.0,
                    "width": 10.0,
                    "height": 10.0,
                    "predict": 9.99
                },
                "input_file": "abcdg.png",
                "output_file": "cdefi.png"
            },
            {
                "p1": {
                    "center_x": 99.0,
                    "center_y": 99.0,
                    "width": 10.0,
                    "height": 10.0,
                    "predict": 9.99
                },
                "p2": {
                    "center_x": 99.0,
                    "center_y": 99.0,
                    "width": 10.0,
                    "height": 10.0,
                    "predict": 9.99
                },
                "input_file": "abcdh.png",
                "output_file": "cdefj.png"
            }]
    }
