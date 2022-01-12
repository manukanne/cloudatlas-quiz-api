from abc import ABC, abstractmethod
from mongoengine import Document
from pydantic import BaseModel
from typing import List, Optional
import json

import schemas
from .models import Category, Quiz, User
from schemas import CategoryInDb as CategoryModel, Quiz as QuizModel, UserInDb as UserModel
from utilities import first_or_default
from auth.utilities import verify_password


class RepositoryBase(ABC):
    """
    Base repository class
    """

    @abstractmethod
    def get(self, key):
        """
        Gets an entity by id/primary key
        :param key: Entity primary key
        :return: Entity object
        """
        ...

    @abstractmethod
    def filter(self, **kwargs):
        """
        Filters an entity
        :param kwargs: Filter operations
        :return: List of entities
        """
        ...

    @abstractmethod
    def persist(self, item):
        """
        Saves or updates an entity
        :param item: Entity to save
        :return: The saved entity
        """
        ...

    @abstractmethod
    def delete(self, item):
        """
        Deletes an entity
        :param item: The entity that should be deleted
        :return: None
        """
        ...


class MongoRepository(RepositoryBase, ABC):
    """
    Base MongoDB repository class
    """

    def __init__(self, dbmodel: Document):
        """
        MongoDB base repository
        :param dbmodel: Orm class type
        """
        self._dbmodel = dbmodel

    def get(self, key):
        return self.filter(pk=key).first()

    def filter(self, **kwargs):
        limit, skip, only = kwargs.pop("limit", 100), kwargs.pop("skip", 0), kwargs.pop("only", None)
        rows = self._dbmodel.objects(**kwargs).skip(skip).limit(limit)
        if only is not None:
            # Issue: Pydantic validates fields -> so if the selected fields do not meet the validation requirements
            # the creation of the domain model fails
            rows.only(*only)
        return rows

    def persist(self, item: Document) -> Document:
        item.save()
        item.reload()
        return item

    def delete(self, item: Document):
        item.delete()


# noinspection PyCallingNonCallable
class DomainRepository(RepositoryBase, ABC):
    """
    Handles the interaction with domain models with the database
    Wrapper class around for MongoDB repository class
    """
    def __init__(self, dbmodel: Document, model: BaseModel):
        """
        Initialites a domain repository
        :param dbmodel: Orm class type
        :param model: Pydantic class type
        """
        self._dbmodel = dbmodel
        self._model = model
        self._repository = MongoRepository(dbmodel)

    def get(self, key) -> BaseModel:
        return first_or_default(self.filter(pk=key))

    def filter(self, **kwargs) -> List[BaseModel]:
        return list(map(lambda x: self._convert2domainmodel(x), self._repository.filter(**kwargs)))

    def _convert2dbmodel(self, item: BaseModel):
        """
        Converts a domain model to a orm model
        :param item: Pydantic domain model
        :return: Converted domain model (orm model)
        """
        return self._dbmodel(**item.dict())

    def _convert2domainmodel(self, item: Document):
        """
        Converts an orm model to a domain model
        :param item: Orm model
        :return: Pydantic domain model
        """
        return self._model.from_orm(item)

    def persist(self, item: BaseModel):
        db_item = self._repository.persist(self._convert2dbmodel(item))
        domain_model = self._convert2domainmodel(db_item)
        return domain_model

    def delete(self, item: BaseModel):
        db_item: Document = self._dbmodel(**item.dict())
        db_item.delete()


# noinspection PyTypeChecker
class UserRepository(DomainRepository):
    """
    Domain user repository
    """
    def __init__(self):
        super(UserRepository, self).__init__(dbmodel=User, model=UserModel)

    def authenticate_user(self, email: str, password: str) -> Optional[UserModel]:
        """
        Validates user credentials
        :param email: User email
        :param password: User plain text password
        :return:
        """
        user: UserModel = self.get(email)
        if user is None:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user


# noinspection PyTypeChecker
class CategoryRepository(DomainRepository):
    """
    Domain category repository
    """
    def __init__(self):
        super().__init__(dbmodel=Category, model=CategoryModel)


# noinspection PyTypeChecker
class QuizRepository(DomainRepository):
    """
    Domain quiz repository
    """
    def __init__(self):
        super().__init__(dbmodel=Quiz, model=QuizModel)

    def _convert2dbmodel(self, item: schemas.Quiz):
        # db_model: Quiz = self._dbmodel(**item.dict()) unable to resolve owner (= current user)
        db_model: Quiz = self._dbmodel(**item.dict(exclude={"owner", "categories"}))
        db_model.owner = User.objects(pk=item.owner).first()
        db_model.categories = [] if item.categories is None or len(item.categories) == 0 else list(
            map(lambda category_id: Category.objects(pk=category_id).first(), item.categories))
        return db_model

    def _convert2domainmodel(self, item: Quiz):
        # MongoDB Document to_json returns just the primary key of referenced documents (e.g owner)
        # use_db_field returns a json in the format of the python document class fields
        # (without this parameter to_json retruns an _id field instead of an identifier field)
        data: dict = json.loads(item.to_json(use_db_field=False))
        return self._model(**data)


class RepositoryContainerBase(ABC):
    """
    Repository container, holds references to all the available repositories
    """
    def __init__(self,
                 category_repository: CategoryRepository,
                 quiz_repository: QuizRepository,
                 user_repository: UserRepository):
        self.category = category_repository
        self.quiz = quiz_repository
        self.user = user_repository


class RepositoryContainer(RepositoryContainerBase):
    def __init__(self):
        super().__init__(
            category_repository=CategoryRepository(),
            quiz_repository=QuizRepository(),
            user_repository=UserRepository()
        )
