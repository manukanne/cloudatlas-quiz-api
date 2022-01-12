from typing import Optional
from fastapi import Depends, HTTPException

import schemas
from orm.repositories import RepositoryContainerBase, RepositoryContainer
from settings import get_settings
from auth import oauth2_scheme, credentials_exception
from auth.utilities import get_username_from_access_token
from schemas import UserInDb


def get_repository_container() -> RepositoryContainerBase:
    """
    Returns the repositoy container that holds all available repositories
    :return: Repository Container
    """
    return RepositoryContainer()


def get_user_from_token(*,
                        token: str = Depends(oauth2_scheme),
                        db: RepositoryContainerBase = Depends(get_repository_container)
                        ) -> Optional[UserInDb]:
    """
    Extracts the current user from the JWT Token
    :param db: Repository Container
    :param token: JWT access token
    :return: Current user
    """
    settings = get_settings()
    username = get_username_from_access_token(token=token,
                                              secret_key=settings.auth_secret_key,
                                              algorithm=settings.auth_algorithm)
    # noinspection PyTypeChecker
    user: Optional[schemas.UserInDb] = db.user.get(username)
    return user


def get_current_active_user(current_user: UserInDb = Depends(get_user_from_token)) -> Optional[UserInDb]:
    """
    Extracts the current user and checks if the user is enabled
    :return: Current active user
    """
    if not current_user or current_user.disabled:
        raise credentials_exception
    return current_user


def common_filter_parameters(skip: int = 0, limit: int = 100) -> dict:
    """
    Provides common query parameters
    :param skip: How many records should be skipped
    :param limit: The maximum item count (only values between 0 and 1000 are allowed)
    :return: Common query parameters dict
    """
    if skip < 0:
        raise HTTPException(status_code=400, detail=f"Value for skip ({skip}) is invalid")
    if limit < 0 or limit > 1000:
        raise HTTPException(status_code=400, detail=f"Value for limit ({limit}) is invalid")
    return {
        "skip": skip,
        "limit": limit
    }
