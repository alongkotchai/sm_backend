from fastapi import (
    Request,
    status,
    HTTPException)
from jwt.exceptions import (
    PyJWTError,
    ExpiredSignatureError)
from core.security import (
    AuthContext,
    Role,
    decode_access_token)
from database import engine


def get_token(req: Request) -> str:
    """Get token from Header bearer token

    Args:
        req (Request): _description_

    Raises:
        HTTPException: _description_

    Returns:
        str: _description_
    """
    try:
        token = req.headers["Authorization"].split(" ")[1]
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized"
        )
    return token


def __validate_token(token: str) -> AuthContext:
    """Validate token, return AuthContext

    Args:
        token (str): jwt string

    Raises:
        HTTPException: _description_

    Returns:
        AuthContext: 
    """
    try:

        return decode_access_token(token)

    except ExpiredSignatureError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token Expired")
    except PyJWTError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized")


def get_auth(req: Request) -> AuthContext:
    """get access token from header and decode it to auth context

    Args:
        req (Request):

    Returns:
        AuthContext:
    """
    return __validate_token(get_token(req))


def get_session():

    if not engine.async_session:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error")
    return engine.async_session
