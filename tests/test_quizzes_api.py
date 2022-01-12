import unittest

from parameterized import parameterized

import schemas
from .fake_client import client, get_auth_client
from .fake_orm_dependicies import get_fake_repository_container


class TestQuizzesApi(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestQuizzesApi, self).__init__(*args, **kwargs)
        self.base_endpoint_name = "quizzes"

    @parameterized.expand([
        [1, 200],
        [100, 404]
    ])
    def test_get_quiz(self, quiz_id: int, status_code: int):
        response = client.get(f"{self.base_endpoint_name}/{quiz_id}")
        assert response.status_code == status_code

    @parameterized.expand([
        [{"title": "Lang"}, 1, 200]
    ])
    def test_read_quizzes(self, query_params: dict, item_count: int, status_code: int):
        response = client.get(f"{self.base_endpoint_name}", params=query_params)
        assert response.status_code == status_code

        if status_code == 200:
            if item_count is not None:
                assert len(response.json()) == item_count

    @parameterized.expand([
        [
            schemas.QuizSubmit(identifier=1, questions=[
                schemas.QuestionSubmit(identifier=1, answers=[
                    schemas.AnswerSubmit(identifier=1, is_correct=True),
                    schemas.AnswerSubmit(identifier=2, is_correct=True),
                    schemas.AnswerSubmit(identifier=3, is_correct=True),
                    schemas.AnswerSubmit(identifier=4, is_correct=False)
                ]
                                       )]), schemas.QuizValidationResult(total_points=3, points=3)
        ],
        [
            schemas.QuizSubmit(identifier=1, questions=[
                schemas.QuestionSubmit(identifier=1, answers=[
                    schemas.AnswerSubmit(identifier=1, is_correct=False),
                    schemas.AnswerSubmit(identifier=2, is_correct=False),
                    schemas.AnswerSubmit(identifier=3, is_correct=False),
                    schemas.AnswerSubmit(identifier=4, is_correct=True)
                ]
                                       )]), schemas.QuizValidationResult(total_points=3, points=0)
        ],
    ])
    def test_validate_quiz(self, quiz_submit: schemas.QuizSubmit, validation_result: schemas.QuizValidationResult):
        response = client.post(f"{self.base_endpoint_name}/validate", json=quiz_submit.dict())
        assert response.status_code == 200
        assert schemas.QuizValidationResult(**response.json()) == validation_result

    @parameterized.expand([
        ["john.doe@gmail.com", "test1234", 200, schemas.QuizUpsert(
            title="Country Quiz",
            description="A quiz about countries",
            categories=[1],
            questions=[schemas.QuestionUpsert(
                title="What is the capital city of Austria?",
                answers=[
                    schemas.AnswerUpsert(answer_text="Vienna", is_correct=True),
                    schemas.AnswerUpsert(answer_text="Innsbruck", is_correct=False),
                    schemas.AnswerUpsert(answer_text="Berlin", is_correct=False),
                    schemas.AnswerUpsert(answer_text="Amsterdam", is_correct=False),
                ]
            )]
        )]
    ])
    def test_create_quiz(self, username: str, password: str, status_code: int, quiz_create: schemas.QuizUpsert):
        auth_client = get_auth_client(username, password)
        response = auth_client.post(f"{self.base_endpoint_name}/", json=quiz_create.dict())
        assert response.status_code == status_code
        if response.status_code == 200:
            db = get_fake_repository_container()
            response_quiz = schemas.Quiz(**response.json())
            db_quiz: schemas.Quiz = db.quiz.get(response_quiz.identifier)
            assert db_quiz.title == response_quiz.title
            assert len(db_quiz.questions) == len(response_quiz.questions)
            assert db_quiz.owner == username
            db.quiz.delete(db_quiz)

    @parameterized.expand([
        ["john.doe@gmail.com", "test1234", 1, schemas.QuizUpsert(
            title="Country Quiz",
            description="A quiz about countries",
            questions=[schemas.QuestionUpsert(
                title="What is the capital city of Austria?",
                answers=[
                    schemas.AnswerUpsert(answer_text="Vienna", is_correct=True),
                    schemas.AnswerUpsert(answer_text="Innsbruck", is_correct=False),
                    schemas.AnswerUpsert(answer_text="Berlin", is_correct=False),
                    schemas.AnswerUpsert(answer_text="Amsterdam", is_correct=False),
                ]
            )]
        ), 200]
    ])
    def test_update_quiz(self,
                         username: str,
                         password: str,
                         quiz_id: int,
                         quiz_update: schemas.QuizUpsert,
                         status_code: int):
        db = get_fake_repository_container()
        db_quiz_before = db.quiz.get(quiz_id)

        auth_client = get_auth_client(username, password)
        response = auth_client.put(f"{self.base_endpoint_name}/{quiz_id}", json=quiz_update.dict())
        assert response.status_code == status_code

        if response.status_code == 200:
            db_quiz: schemas.Quiz = db.quiz.get(quiz_id)
            response_quiz = schemas.Quiz(**response.json())
            db.quiz.persist(db_quiz_before)
            # Validate Quiz
            assert db_quiz.identifier == response_quiz.identifier
            assert response_quiz.title == quiz_update.title
            assert response_quiz.description == quiz_update.description

            for request_question, response_question in zip(quiz_update.questions, response_quiz.questions):
                # Validate Questions
                assert request_question.title == response_question.title
                for request_answer, response_answer in zip(request_question.answers, response_question.answers):
                    # Validate Answers
                    assert request_answer.answer_text == response_answer.answer_text
                    assert request_answer.is_correct == response_answer.is_correct

    @parameterized.expand([
        ["tony.stark@gmail.com", "test1234", 3, 401],
        ["john.doe@gmail.com", "test1234", 123, 404],
        ["john.doe@gmail.com", "test1234", 3, 200]
    ])
    def test_delete_quiz(self, username: str, password: str, quiz_id: int, status_code: int):
        auth_client = get_auth_client(username, password)
        response = auth_client.delete(f"{self.base_endpoint_name}/{quiz_id}")

        assert response.status_code == status_code
