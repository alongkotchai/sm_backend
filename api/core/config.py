from pydantic_settings import BaseSettings
from pydantic import (
    MySQLDsn,
    Field,
    IPvAnyAddress
)
from dotenv import load_dotenv

# load enviroment varibles in env files
load_dotenv()


class Setting(BaseSettings):
    """
        Class represent Service setting parameters
    """
    MYSQL_DSN: MySQLDsn = Field(
        default="mysql+aiomysql://root:devpass@localhost/api?charset=utf8mb4")
    SECRET_AUTH: str = Field(default='hello_world')
    SECRET_REFRESH: str = Field(default='hello_world')
    ACCESS_EXPIRE_HOUR: int = Field(default=1, min=1, max=24)
    SERVICE_HOST: IPvAnyAddress = Field(default='127.0.0.1')
    SERVICE_PORT: int = Field(min=1, max=65536, default=50505)
    NUMBER_WORKER: int = Field(min=1, max=8, default=4)


setting = Setting()
