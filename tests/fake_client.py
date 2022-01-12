from fastapi.testclient import TestClient

from app import app
from dependencies import get_repository_container
from .fake_orm_dependicies import get_fake_repository_container

# Dependicy injection -> inject fake database repository container
app.dependency_overrides[get_repository_container] = get_fake_repository_container

# creates a client object with no authentication headers
client = TestClient(app)


def get_auth_client(username: str, password: str, token_endpoint: str = "/users/token") -> TestClient:
    """
    Creates a FastAPI testclient and includes the bearer token in the header.
    If the provided credentials are invalid, no bearer token is included.
    :param username: User email
    :param password: Plaintext password
    :param token_endpoint: URL of the token endpoint
    :return: FastAPI testclient
    """
    auth_client = TestClient(app)
    response = auth_client.post(token_endpoint,
                                headers={"Content-Type": "application/x-www-form-urlencoded"},
                                data={"username": username, "password": password})
    if response.status_code == 200:
        access_token = response.json().get("access_token")
        auth_client.headers = {
           "Authorization": f"Bearer {access_token}"
        }
    return auth_client

