from fastapi import APIRouter, Depends, HTTPException
from typing import List

from dependencies import get_repository_container, common_filter_parameters, get_current_active_user
from orm.repositories import RepositoryContainerBase
import schemas

router = APIRouter(
    prefix="/categories",
    tags=["categories"]
)


@router.post("/", response_model=schemas.CategoryInDb)
def create_category(category: schemas.CategoryUpsert,
                    current_user: schemas.UserInDb = Depends(get_current_active_user),
                    db: RepositoryContainerBase = Depends(get_repository_container)):
    """
    Endpoint for creating a category entity.
    :param category: Category data
    :param current_user: Current user
    :param db: Repository container
    :return: Returns the created category
    """
    if len(db.category.filter(title=category.title)) == 0:
        return db.category.persist(category)
    raise HTTPException(status_code=400, detail="Category already exists")


@router.delete("/{category_id}")
def delete_category(category_id: int,
                    current_user: schemas.UserInDb = Depends(get_current_active_user),
                    db: RepositoryContainerBase = Depends(get_repository_container)):
    """
    Deletes an unused category
    :param category_id: ID of the to be deleted category
    :param current_user: Current user
    :param db: Repository container
    :return: 200 if OK
    """
    category_del = db.category.get(category_id)
    if category_del is None:
        raise HTTPException(status_code=404, detail="Category does not exists")

    # quizzes = db.quiz.filter(categories=category_id, only=["identifier"])

    quizzes = db.quiz.filter(categories__in=[category_id])
    if len(quizzes) > 0:
        raise HTTPException(status_code=400, detail="Category is in use, unable to delete category")
    db.category.delete(category_del)
    return 200


@router.get("/", response_model=List[schemas.CategoryInDb])
def read_categories(title: str = None, description: str = None, commons=Depends(common_filter_parameters),
                    db: RepositoryContainerBase = Depends(get_repository_container)):
    """
    Endpoint for quering categories
    :param title: Returns all categories that contain the search value in the title
    :param description: Returns all categories that contain the search value in the description
    :param commons: Common filter parameters
    :param db:Repository Container
    :return: List of retrieved categories
    """
    db_query_params = dict(commons)

    if title:
        db_query_params["title__icontains"] = title

    if description:
        db_query_params["description__icontains"] = description

    return db.category.filter(**db_query_params)


@router.get("/{category_id}", response_model=schemas.CategoryInDb)
def read_category(category_id: int, db: RepositoryContainerBase = Depends(get_repository_container)):
    """
    Gets a category by ID
    :param category_id: Category ID
    :param db: Repository Container
    :return: Category
    """
    category = db.category.get(category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category does not exists")
    return category
