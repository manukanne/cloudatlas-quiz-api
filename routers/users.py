from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

import schemas
from settings import get_settings
from dependencies import get_repository_container, get_current_active_user
from orm.repositories import RepositoryContainerBase
from auth import credentials_exception
from auth.utilities import create_access_token

router = APIRouter(
    prefix="/users",
    tags=["user"]
)


@router.post("/token", response_model=schemas.Token)
def token(db: RepositoryContainerBase = Depends(get_repository_container),
          form_data: OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm)):
    """
    OAUTH2 token endpoint
    :param db: Repository Container
    :param form_data: OAUTH2 form data (contains username & password)
    :return: JWT token
    """
    user: schemas.UserInDb = db.user.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise credentials_exception
    settings = get_settings()
    access_token = create_access_token(data={"sub": user.email},
                                       secret_key=settings.auth_secret_key,
                                       algorithm=settings.auth_algorithm)
    return schemas.Token(access_token=access_token, token_type="bearer")


@router.post("/signup", response_model=schemas.User)
def signup(user_signup: schemas.UserUpsert, db: RepositoryContainerBase = Depends(get_repository_container)):
    """
    Endpoint for user signup/registration
    :param user_signup: User signup data
    :param db: Repository Container
    :return: Returns the created user
    """
    if db.user.get(user_signup.email) is not None:
        raise HTTPException(status_code=400, detail="User already exists")
    user = schemas.UserInDb(**user_signup.dict(exclude={"password"}),
                            disabled=False,
                            password_hash=user_signup.password)
    return db.user.persist(user)


@router.get("/me", response_model=schemas.User)
def get_current_user(current_user: schemas.UserInDb = Depends(get_current_active_user)):
    """
    Gets the user information of the current logged-in user
    :param current_user: Current user
    :return: Information about the current user
    """
    return current_user
