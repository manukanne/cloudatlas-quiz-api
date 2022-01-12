from typing import List, Optional
from pydantic import BaseModel, validator, ValidationError
import re

from auth.utilities import get_password_hash


# User models
class User(BaseModel):
    email: str
    first_name: str
    last_name: str

    # noinspection PyMethodParameters
    @validator("email")
    def valid_email(cls, v):
        """
        Pydantic Validation -> Checks if an email has a valid format
        :param v: Email value
        :return: Email
        """
        regex = re.compile(
            r"([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\"([]!#-[^-~ \t]|(\\[\t -~]))+\")@([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\[[\t -Z^-~]*])")
        if not re.fullmatch(regex, v):
            raise ValidationError("Email is not valid!")
        return v


class UserInDb(User):
    disabled: Optional[bool] = None
    password_hash: str

    class Config:
        orm_mode = True


class UserUpsert(User):
    password: str

    # noinspection PyMethodParameters
    @validator("password")
    def password_compliance_check(cls, v):
        """
        Pydantic Validation -> checks if a password meets the security compliances (like password length etc.)
        :param v: Plaintext password
        :return: Returns the hashed password
        """
        if not v:
            return None

        if len(v) < 8:
            raise ValidationError("Password should have at least 8 characters")
        if re.search(r"\d", v) is None:
            raise ValidationError("Password should contain numbers")
        if re.search(r"[A-Z]", v) is None:
            raise ValidationError("Password should contain upper case letters")
        if re.search(r"[ !#$%&'()*+,-./[\\\]^_`{|}~" + r'"]', v) is None:
            raise ValidationError("Password should contain symbols")
        return get_password_hash(v)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(Token):
    email: Optional[str] = None


# Category schemas
class CategoryBase(BaseModel):
    title: str
    description: Optional[str] = None


class CategoryUpsert(CategoryBase):
    ...


class CategoryInDb(CategoryBase):
    identifier: Optional[int]

    class Config:
        orm_mode = True


# Answer schemas
class AnswerBase(BaseModel):
    answer_text: str
    is_correct: bool


class AnswerUpsert(AnswerBase):
    ...


class Answer(AnswerBase):
    identifier: Optional[int]

    class Config:
        orm_mode = True


# Question schemas
class QuestionBase(BaseModel):
    title: str


class QuestionUpsert(QuestionBase):
    answers: List[AnswerUpsert] = []

    @validator("answers", each_item=False)
    def answer_validation(cls, answers_check: List[AnswerUpsert]):
        """
        Pydantic Validation -> checks if at least one correct answer is provided
        :param answers_check: List of answers
        :return: Returns the validated answers
        """
        correct_answer_ct = sum([1 for a in answers_check if a.is_correct])
        if correct_answer_ct == 0:
            raise ValidationError("At least one correct answer is required")
        return answers_check


class Question(QuestionBase):
    identifier: Optional[int]
    answers: List[Answer]

    class Config:
        orm_mode = True


# Quiz schemas
class QuizBase(BaseModel):
    title: str
    description: Optional[str] = None
    categories: Optional[List[int]] = []


class QuizUpsert(QuizBase):
    questions: List[QuestionUpsert] = []

    @validator("categories", each_item=False)
    def categories_validator(cls, categories: List[int]):
        """
        Pydantic Validation -> checks if a maximum of 3 categories is provided
        :param categories: List of category ids
        :return: Returns the validated category ids
        """
        if len(categories) > 3:
            raise ValidationError("Please specify only a maximum of 3 categories")
        return categories

    @validator("questions", each_item=False)
    def questions_validator(cls, questions: List[QuestionUpsert]):
        """
        Pydantic Validation -> checks if at least one question is provided
        :param questions: List of questions
        :return: Returns the validated questions
        """
        if len(questions) == 0:
            raise ValidationError("Please specify at least one question")
        return questions


class Quiz(QuizBase):
    identifier: Optional[int]
    questions: List[Question] = []
    owner: str

    class Config:
        orm_mode = True


# Quiz Submit Models
class AnswerSubmit(BaseModel):
    identifier: int
    is_correct: bool


class QuestionSubmit(BaseModel):
    identifier: int
    answers: List[AnswerSubmit] = []


class QuizSubmit(BaseModel):
    identifier: int
    questions: List[QuestionSubmit] = []


class QuizValidationResult(BaseModel):
    total_points: int
    points: int
