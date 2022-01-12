import unittest
from parameterized import parameterized
import schemas

from .fake_client import client, get_auth_client
from .fake_orm_dependicies import get_fake_repository_container


class TestUsersApi(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestUsersApi, self).__init__(*args, **kwargs)
        self.base_endpoint_name = "users"

    @parameterized.expand([
        [{"username": "john.doe@gmail.com", "password": "test1234"}, 200],
        [{"username": "john.doe@gmail.com", "password": "invalid_password"}, 401],
        [{"username": "test", "password": "skjhsdhsjk"}, 401]
    ])
    def test_login(self, data, status_code):
        response = client.post(f"/{self.base_endpoint_name}/token", headers={
            "Content-Type": "application/x-www-form-urlencoded"
        }, data=data)
        assert response.status_code == status_code

    @parameterized.expand([
        ["john.doe@gmail.com", "test1234", 200],
        ["test@gmail.com", "hdjhsh", 401]
    ])
    def test_user_me(self, username: str, password: str, status_code: int):
        auth_client = get_auth_client(username, password)
        response = auth_client.get(f"/{self.base_endpoint_name}/me")
        assert response.status_code == status_code

        if response.status_code == 200:
            me = schemas.User(**response.json())
            assert me.email == username

    # Cannot use pydantic models as test parameters -> if the pdydantic validation fails, the test is not executed
    @parameterized.expand([
        # Invalid password -> password does not meet the security compiliance checks
        [{"email": "john.wick@gmail.com", "first_name": "John", "last_name": "Wick", "password": "Daisy"}, 422],
        # Invalid email -> email has no valid format
        [{"email": "test", "first_name": "Test", "last_name": "Test", "password": "SecuryPassword1234$"}, 422],
        [{"email": "john.wick@gmail.com", "first_name": "John", "last_name": "Wick", "password": "Daisy2022!"}, 200]
    ])
    def test_user_signup(self, user_signup_data: dict, status_code: int):
        response = client.post(f"/{self.base_endpoint_name}/signup", json=user_signup_data)
        assert response.status_code == status_code
        if status_code == 200:
            me = schemas.User(**response.json())
            email, first_name, last_name = user_signup_data.get("email"), user_signup_data.get(
                "first_name"), user_signup_data.get("last_name")
            assert me.email == email
            assert me.first_name == first_name
            assert me.last_name == last_name
            db = get_fake_repository_container()
            user_del = db.user.get(user_signup_data.get("email"))
            db.user.delete(user_del)
