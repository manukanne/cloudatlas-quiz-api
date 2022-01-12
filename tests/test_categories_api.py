import unittest
from parameterized import parameterized

import schemas
from .fake_client import client, get_fake_repository_container, get_auth_client


class TestCategoriesApi(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestCategoriesApi, self).__init__(*args, **kwargs)
        self.base_endpoint_name = "categories"

    @parameterized.expand([
        [1, 200],
        [2, 200],
        [3, 404]
    ])
    def test_get_category(self, category_id, status_code):
        response = client.get(f"{self.base_endpoint_name}/{category_id}")
        assert int(response.status_code) == status_code

    @parameterized.expand([
        [0, 2, 2],
        [0, 1, 1]
    ])
    def test_get_categories(self, skip, limit, length):
        response = client.get(f"{self.base_endpoint_name}/", params={"skip": skip, "limit": limit})
        assert len(response.json()) == length

    @parameterized.expand([
        ["john.doe@gmail.com", "test1234", schemas.CategoryUpsert(title="Category1", description="Category1 desc"),
         200],
        ["john.doe@gmail.com", "test1234", schemas.CategoryUpsert(title="Category2", description="Category2 desc"),
         200],
        ["john.doe@gmail.com", "test1234", schemas.CategoryUpsert(title="Fun", description="Some description"), 400]
    ])
    def test_create_categories(self, username: str, password: str, category: schemas.CategoryUpsert, status_code: int):
        auth_client = get_auth_client(username, password)
        response = auth_client.post(f"{self.base_endpoint_name}/", json=category.dict())
        assert response.status_code == status_code

        if response.status_code == 200:
            db = get_fake_repository_container()
            db.category.delete(category)

    @parameterized.expand([
        ["john.doe@gmail.com", "test1234", 2, 400],
        ["john.doe@gmail.com", "test1234", 3, 200],
        ["john.doe@gmail.com", "test1234", 1001, 404],
    ])
    def test_delete_category(self, username: str, password: str, category_id: int, status_code: int):
        auth_client = get_auth_client(username, password)
        respone = auth_client.delete(f"{self.base_endpoint_name}/{category_id}")
        assert respone.status_code == status_code
