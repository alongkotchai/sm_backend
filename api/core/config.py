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
    MYSQL_DSN: MySQLDsn = Field()
    SECRET_AUTH: str = Field(default='hello_world')
    ACCESS_EXPIRE_HOUR: int = Field(default=1, min=1, max=24)
    SERVICE_HOST: IPvAnyAddress = Field(default='127.0.0.1')
    SERVICE_PORT: int = Field(min=1, max=65536, default=50505)


setting = Setting()
