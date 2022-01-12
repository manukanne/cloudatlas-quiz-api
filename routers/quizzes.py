from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional

from dependencies import get_repository_container, get_current_active_user, common_filter_parameters
from orm.repositories import RepositoryContainerBase
import services
import schemas

router = APIRouter(
    prefix="/quizzes",
    tags=["quizzes"]
)


def check_if_categories_exists(db: RepositoryContainerBase, category_ids: List[int]):
    """
    Checks if a list of categories exists. Raises an HTTP exeption if one of the provided ID's does not exist
    :param db: Repository container
    :param category_ids: List of categories ID's
    :return: None
    """
    for category_id in category_ids:
        if db.category.get(category_id) is None:
            raise HTTPException(status_code=404, detail=f"Category with {category_id} does not exists")


@router.get("/", response_model=List[schemas.Quiz])
def read_quizzes(title: str = None,
                 description: str = None,
                 owner_email: str = None,
                 categories: List[int] = Query(None),
                 commons=Depends(common_filter_parameters),
                 db: RepositoryContainerBase = Depends(get_repository_container)):
    """
    Endpoint for quering quizzes
    :param title: Returns all quizzes that contain the search value in the title
    :param description: Returns all quizzes that contain the search value in the description
    :param owner_email: Returns all quizess which are owned by the provided user
    :param categories: List of categories -> returns all
    :param commons: Returns all quizzes that contain one or more of the provided category IDs.
    :param db: Repository Container
    :return: List of retrieved categories
    """
    db_query_params = dict(commons)

    if categories:
        db_query_params["categories__in"] = categories
    if title:
        db_query_params["title__icontains"] = title
    if description:
        db_query_params["description__icontains"] = description
    if owner_email:
        db_query_params["owner"] = owner_email

    return db.quiz.filter(**db_query_params)


@router.get("/{quiz_id}", response_model=schemas.Quiz)
def read_quiz(quiz_id: int, db: RepositoryContainerBase = Depends(get_repository_container)):
    """
    Gets a quiz by id
    :param quiz_id: Quiz ID
    :param db: Repository Container
    :return: Quiz
    """
    quiz = db.quiz.get(quiz_id)
    if quiz is None:
        raise HTTPException(status_code=404, detail="Quiz does not exists")
    return quiz


@router.post("/", response_model=schemas.Quiz)
def create_quiz(quiz: schemas.QuizUpsert,
                current_user: schemas.UserInDb = Depends(get_current_active_user),
                db: RepositoryContainerBase = Depends(get_repository_container)):
    """
    Creates a quiz
    :param quiz: Quiz data
    :param current_user: Current user
    :param db: Repository Container
    :return: Returns the created quiz
    """
    check_if_categories_exists(db, quiz.categories)
    db_quiz = schemas.Quiz(**quiz.dict(), owner=current_user.email)
    return db.quiz.persist(db_quiz)


@router.put("/{quiz_id}", response_model=schemas.Quiz)
def update_quiz(quiz_id: int,
                quiz_update: schemas.QuizUpsert,
                current_user: schemas.UserInDb = Depends(get_current_active_user),
                db: RepositoryContainerBase = Depends(get_repository_container)):
    """
    Updates/ Overwrites a quiz by ID
    :param quiz_id: Quiz ID
    :param quiz_update: Quiz update data
    :param current_user: Current user
    :param db: Container Repository
    :return: Returns the updated quiz
    """
    quiz: schemas.Quiz = db.quiz.get(quiz_id)
    if quiz is None:
        raise HTTPException(status_code=404, detail="Quiz does not exists")
    if quiz.owner != current_user.email:
        raise HTTPException(status_code=401)
    check_if_categories_exists(db, quiz.categories)
    # Does not work, creates an object of type QuizUpsert and not of type Quiz
    # update_dict = quiz_update.dict()
    # quiz_updated: schemas.Quiz = quiz.copy(update=update_dict, deep=True)

    db_quiz_update = schemas.Quiz(**quiz_update.dict(), owner=current_user.email)
    db_quiz_update.identifier = quiz.identifier

    return db.quiz.persist(db_quiz_update)


@router.post("/validate", response_model=schemas.QuizValidationResult)
def validate_quiz(quiz_submit: schemas.QuizSubmit,
                  db: RepositoryContainerBase = Depends(get_repository_container)):
    """
    Validates a quiz and returns the reached points
    :param quiz_submit: Quiz submit data
    :param db: Repository Container
    :return: Quiz validation result (total points and reached points)
    """
    # noinspection PyTypeChecker
    quiz: schemas.Quiz = db.quiz.get(quiz_submit.identifier)
    if quiz is None:
        raise HTTPException(status_code=404, detail="Quiz does not exists")

    validation_result = services.validate_quiz(quiz, quiz_submit)
    if validation_result is None:
        raise HTTPException(status_code=400)

    return validation_result


@router.delete("/{quiz_id}")
def delete_quiz(quiz_id: int,
                current_user: schemas.UserInDb = Depends(get_current_active_user),
                db: RepositoryContainerBase = Depends(get_repository_container)):
    """
    Deletes a quiz by ID. A user has to be the owner of the quiz, otherwise this endpoint returns a 401 code
    :param quiz_id: Quiz ID
    :param db: Repository Container
    :param current_user: Current User
    :return: 200 if OK
    """
    quiz_del = db.quiz.get(quiz_id)
    if quiz_del is None:
        raise HTTPException(status_code=404, detail="Quiz does not exists")
    if quiz_del.owner != current_user.email:
        raise HTTPException(status_code=401)
    db.quiz.delete(quiz_del)
    return 200
