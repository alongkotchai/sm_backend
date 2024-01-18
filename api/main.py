import time
import logging
from contextlib import asynccontextmanager
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from fastapi import (
    Request,
    FastAPI,
    status)
import uvicorn
from core.config import setting
from database import (
    models,
    engine)
from controllers import (
    auth,
    users)

logger = logging.getLogger(__name__)


async def setup_db() -> None:
    """
        Initial databases connection session
    """

    async_eng, async_session = await engine.init_engine(str(setting.MYSQL_DSN))

    logger.info("Starting MySql connection")
    async with async_eng.begin() as conn:
        logger.info("Createing tables")
        await conn.run_sync(models.Base.metadata.create_all)
    engine.async_session = async_session
    engine.engine = async_eng
    await engine.ping_db(async_session)
    logger.info("Successfully connect to MySql database")


async def init_root_user() -> None:
    """
        Create a root user is not existed
    """
    await users.__create_default_user(engine.async_session)


async def close_db_connection() -> None:
    """
        Dispose engine
    """

    await engine.dispose_engine(engine.engine)
    logger.info('close MySQL conntection')


@asynccontextmanager
async def lifespan(app: FastAPI):
    # run before api service start
    await setup_db()
    await init_root_user()
    yield
    # run after service closing
    await close_db_connection()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# # service rounters
app.include_router(auth.router)
app.include_router(users.router)


# override exception error response

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
        request: Request, exc: RequestValidationError):
    '''Default Error for Request Validation'''

    detail = ""
    typ = "body_error"
    typ = exc.errors()[0]['type']
    detail = '.'.join(map(str, exc.errors()[0]['loc'])) + \
        ' >> ' + exc.errors()[0]['msg']
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={'type': typ, 'detail': detail}
    )

# default error response for sqlalchemy error


@app.exception_handler(SQLAlchemyError)
async def validation_exception_handler(
        request: Request, exc: SQLAlchemyError):
    '''Default Error for sqlalchemy error'''
    print(exc)
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={'detail': 'internal service not response'}
    )


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    ''' calculate process time for each request'''

    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


if __name__ == "__main__":
    # start serving
    uvicorn.run('main:app',
                host=str(setting.SERVICE_HOST),
                port=setting.SERVICE_PORT,
                log_config="./static/logs/log_conf.yml",
                reload=True)
