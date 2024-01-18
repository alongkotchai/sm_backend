from uuid import UUID
from typing import Optional
from enum import Enum
from datetime import (
    datetime,
    timedelta)
from pydantic import (
    BaseModel,
    Field)
import jwt
import bcrypt
from core.config import setting


class Role(str, Enum):
    """
        enum represent all roles of user
    """
    ADMIN = 'ADMIN'
    USER = 'USER'


class AuthContext(BaseModel):
    """
        context for authorization user
    """
    sub: UUID
    role: Role = Field(default=Role.USER)


def create_access_token(
    auth_context: AuthContext,
    expire_priod: timedelta = None,
) -> str:
    """create a jwt access token

    Args:
        auth_context (AuthContext):
        expire_priod (timedelta, optional): period for jwt to expire. Default from setting.

    Returns:
        token (str): access_token
    """
    if expire_priod:
        expire = datetime.utcnow() + expire_priod
    else:
        expire = datetime.utcnow() + timedelta(
            hours=setting.ACCESS_EXPIRE_HOUR)
    token = jwt.encode({'exp': expire,
                        'role': auth_context.role,
                        'sub': auth_context.sub.hex},
                       algorithm='HS256',
                       key=setting.SECRET_AUTH)
    return token


def decode_access_token(token: str) -> AuthContext:
    """decode access jwt with 'secret_auth' key

    Args:
        token (str): jwt

    Returns:
        Optional[AuthContext]: 
    """
    auth = jwt.decode(jwt=token,
                      key=setting.SECRET_AUTH,
                      algorithms=['HS256'])
    return AuthContext(sub=auth.get('sub'),
                       role=auth.get('role'))


def hash_password(password: str) -> str:

    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def compare_hash(password: str, hash: str):

    return bcrypt.checkpw(password.encode(), hash.encode())
