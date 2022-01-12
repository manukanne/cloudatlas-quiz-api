from datetime import timedelta, datetime
from typing import Optional
# noinspection PyPackageRequirements
from jose import jwt, JWTError, ExpiredSignatureError
# noinspection PyPackageRequirements
from jose.exceptions import JWTClaimsError

from . import pwd_context, credentials_exception


def verify_password(plain_password, hashed_password):
    """
    Validates a plain text password with a hashed password
    :param plain_password: Plain text user password
    :param hashed_password: Hashed user password (from DB)
    :return: True or False
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """
    Calculates the password hash
    :param password: Plain text password
    :return: Password hash
    """
    return pwd_context.hash(password)


def create_access_token(*, data: dict, secret_key: str, algorithm: str, expires_delta: Optional[timedelta] = None):
    """

    :param data: Data that should be included in the access token
    :param secret_key: The secret key that should be used for token encoding
    :param algorithm: The algorith that should be used for token encoding (like HS256)
    :param expires_delta: Lifetime timespan of the token (default is 90 min)
    :return: JWT access token
    """
    to_encode = data.copy()
    if not expires_delta:
        expire = datetime.utcnow() + timedelta(minutes=90)
    else:
        expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt


def get_username_from_access_token(token: str, secret_key: str, algorithm: str) -> Optional[str]:
    """
    Decodes a token and returns the "sub" (= username) of the decoded token
    :param token: JWT access token
    :param secret_key: The secret key that should be used for token decoding
    :param algorithm: The algorith that should be used for token decoding (like HS256)
    :return: Username
    """
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        username: str = payload.get("sub")
        if not username:
            raise credentials_exception
        return username
    except (JWTError, ExpiredSignatureError, JWTClaimsError):
        raise credentials_exception
