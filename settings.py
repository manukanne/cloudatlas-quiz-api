from pydantic import BaseSettings
from functools import lru_cache


class ApiSettings(BaseSettings):
    """
    API Settings from .env file
    """
    auth_secret_key: str
    auth_algorithm: str
    mongodb_conn_str: str

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> ApiSettings:
    """
    Returns the cached API settins
    :return: API settings
    """
    return ApiSettings()
