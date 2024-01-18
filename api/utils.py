from random import choices
from string import ascii_letters, digits
import re
CHARS = ascii_letters + digits


def random_string(length: int = 1) -> str:
    """generate a random string of asccii charecters and number

    Args:
        length (int, optional): lenght of random string. Defaults to 1.

    Returns:
        str: random string of asccii charecters and number
    """
    return ''.join(choices(CHARS, k=length))


def validate_pass(password: str) -> None:
    """validate if passsword is strong enough

    Args:
        password (str):

    Raises:
        ValueError:
    """
    if ' ' in password:
        raise ValueError('password cannot contain any space')
    if not re.match("^(?=.*?[A-Z]).{1,}$", password):
        raise ValueError('password must contain uppercase character')
    if not re.match("^(?=.*?[a-z]).{1,}$", password):
        raise ValueError('password must contain lowercase character')
    if not re.match("^(?=.*?[0-9]).{1,}$", password):
        raise ValueError('password must contain number')
    if not re.match("^(?=.*?[#?!@$%^&*-]).{1,}$", password):
        raise ValueError('password must contain spacial character')
