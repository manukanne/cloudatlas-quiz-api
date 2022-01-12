from pydantic import BaseModel
from typing import List
from abc import ABC
from random import randrange

from orm.repositories import RepositoryBase, UserRepository, QuizRepository, CategoryRepository, RepositoryContainerBase
from utilities import first_or_default
import schemas


def id_generator():
    """
    Genereates random database ids (normally this would be handled by the database)
    :return: Random integer ID between 1000 and 100.000.000
    """
    return randrange(1000, 100_000_000)


class FakeRepository(RepositoryBase, ABC):
    """
    Fake in-memory database repository base class
    """

    def __init__(self):
        self._db_storage: List[BaseModel] = []

    def filter(self, **kwargs):
        limit, skip, only = kwargs.pop("limit", 100), kwargs.pop("skip", 0), kwargs.pop("only", None)

        # Remove MongoEngine specific query operators
        # If testing for specific operator is required, extract the operator and
        # perform the required filtering operation on the list
        del_keys = []
        in_operators = []
        icontains_operators = []
        for k, v in kwargs.items():
            if "__in" in k:
                in_operators.append((k.replace("__in", ""), v))
            if "__icontains" in k:
                icontains_operators.append((k.replace("__icontains", ""), v))
            if "__" in k:
                del_keys.append(k)
        for k in del_keys:  # Remove all filtering operations from kwargs
            del kwargs[k]

        rows = [x for x in self._db_storage[skip: limit] if all(getattr(x, k) == v for k, v in kwargs.items())]

        # Perform Mongoengine "in" operator
        for in_op in in_operators:
            k, v = in_op
            if isinstance(v, list):
                rows = [row for row in rows if any(item in getattr(row, k) for item in v)]
        # Perform Mongoengine "icontains" operator
        for icontains_op in icontains_operators:
            k, v = icontains_op
            if isinstance(v, str):
                rows = [row for row in rows if v.lower() in getattr(row, k).lower()]

        return rows

    def persist(self, item: BaseModel):
        update = False
        for idx, list_item in enumerate(self._db_storage):
            if list_item == item:
                self._db_storage[idx] = item
                update = True
        if not update:
            self._db_storage.append(item)
        return item

    def delete(self, item: BaseModel):
        self._db_storage.remove(item)


class FakeCategoryRepository(FakeRepository, CategoryRepository):
    def get(self, key):
        return first_or_default(self.filter(identifier=key))


class FakeQuizRepository(FakeRepository, QuizRepository):
    def get(self, key):
        return first_or_default(self.filter(identifier=key))

    def persist(self, item: schemas.Quiz, skip_id_generation=False):
        update: bool = self.get(item.identifier) is not None
        if not update and not skip_id_generation:
            item.identifier = id_generator()

        # Generate random ids for nested entities (if no ids are provided)
        for q in item.questions:
            q.identifier = q.identifier or id_generator()
            for a in q.answers:
                a.identifier = a.identifier or id_generator()
        return super(FakeQuizRepository, self).persist(item)


class FakeUserRepository(FakeRepository, UserRepository):
    def get(self, key):
        return first_or_default(self.filter(email=key))


# Add some fake data

# ------------------ Fake category data ------------------
fake_category_repository = FakeCategoryRepository()
fake_category_repository.persist(schemas.CategoryInDb(identifier=1, title="Fun", description="A funny category"))
fake_category_repository.persist(
    schemas.CategoryInDb(identifier=2, title="Programming", description="A programming category"))
fake_category_repository.persist(
    schemas.CategoryInDb(identifier=3, title="Del Category", description="Category deletion test"))

# ------------------ Fake quiz data ------------------
fake_quiz_respository = FakeQuizRepository()
fake_quiz_respository.persist(schemas.Quiz(
    identifier=1,
    title="Quiz 1",
    # owner=schemas.User(email="john.doe@gmail.com", first_name="John", last_name="Wick"),
    owner="john.doe@gmail.com",
    categories=[2],
    questions=[
        schemas.Question(
            identifier=1,
            title="In which languages is MongoDB implemented?",
            answers=[
                schemas.Answer(identifier=1, answer_text="C++", is_correct=True),
                schemas.Answer(identifier=2, answer_text="JavaScript", is_correct=True),
                schemas.Answer(identifier=3, answer_text="Python", is_correct=True),
                schemas.Answer(identifier=4, answer_text="Java", is_correct=False)
            ]
        )
    ]
), skip_id_generation=True)

fake_quiz_respository.persist(schemas.Quiz(
    identifier=2,
    title="Language Quiz 1",
    # owner=schemas.User(email="john.doe@gmail.com", first_name="John", last_name="Wick"),
    owner="john.doe@gmail.com",
    categories=[1],
    questions=[
        schemas.Question(
            identifier=2,
            title="What is the official language in Austria",
            answers=[
                schemas.Answer(identifier=5, answer_text="German", is_correct=True),
                schemas.Answer(identifier=6, answer_text="English", is_correct=False),
                schemas.Answer(identifier=7, answer_text="Spanish", is_correct=False),
                schemas.Answer(identifier=8, answer_text="French", is_correct=False)
            ]
        )
    ]
), skip_id_generation=True)

fake_quiz_respository.persist(schemas.Quiz(
    identifier=3,
    title="Delete Test",
    # owner=schemas.User(email="john.doe@gmail.com", first_name="John", last_name="Wick"),
    owner="john.doe@gmail.com",
    categories=[1],
    questions=[
        schemas.Question(
            identifier=3,
            title="What is the official language in Austria",
            answers=[
                schemas.Answer(identifier=9, answer_text="German", is_correct=True),
                schemas.Answer(identifier=10, answer_text="English", is_correct=False),
                schemas.Answer(identifier=11, answer_text="Spanish", is_correct=False),
                schemas.Answer(identifier=12, answer_text="French", is_correct=False)
            ]
        )
    ]
), skip_id_generation=True)

# ------------------ Fake user data ------------------
fake_user_repository = FakeUserRepository()
fake_user_repository.persist(schemas.UserInDb(
    email="john.doe@gmail.com",
    first_name="John",
    last_name="Doe",
    disabled=False,
    password_hash="$2b$12$IHnKcvOXll5.809cW.fgC.jvh3HCc3HX4rkH8.LYd0VDuhPnwZ0gC"  # pwd is test1234
))
fake_user_repository.persist(schemas.UserInDb(
    email="tony.stark@gmail.com",
    first_name="Tony",
    last_name="Stark",
    disabled=False,
    password_hash="$2b$12$IHnKcvOXll5.809cW.fgC.jvh3HCc3HX4rkH8.LYd0VDuhPnwZ0gC"  # pwd is test1234
))


class FakeRepositoryContainer(RepositoryContainerBase):
    """
    Fake repository container
    """

    def __init__(self):
        super().__init__(
            category_repository=fake_category_repository,
            quiz_repository=fake_quiz_respository,
            user_repository=fake_user_repository
        )


def get_fake_repository_container():
    """
    Fake dependicy injection method for the fake repository container
    :return: Fake repository container
    """
    return FakeRepositoryContainer()
