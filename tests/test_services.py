import unittest
from parameterized import parameterized

import schemas
import services

quiz_data = schemas.Quiz(
    identifier=1,
    title="Quiz 1",
    # owner=schemas.User(email="john.doe@gmail.com", first_name="John", last_name="Wick"),
    owner = "john.doe@gmail.com",
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
)

submit1_data = schemas.QuizSubmit(
    identifier=1,
    questions=[
        schemas.QuestionSubmit(
            identifier=1,
            answers=[
                schemas.AnswerSubmit(identifier=1, is_correct=True),
                schemas.AnswerSubmit(identifier=2, is_correct=True),
                schemas.AnswerSubmit(identifier=3, is_correct=True),
                schemas.AnswerSubmit(identifier=4, is_correct=False)
            ]
        )
    ]
)

submit2_data = schemas.QuizSubmit(
    identifier=1,
    questions=[
        schemas.QuestionSubmit(
            identifier=1,
            answers=[
                schemas.AnswerSubmit(identifier=1, is_correct=True),
                schemas.AnswerSubmit(identifier=2, is_correct=False),
                schemas.AnswerSubmit(identifier=3, is_correct=False),
                schemas.AnswerSubmit(identifier=4, is_correct=False)
            ]
        )
    ]
)

submit3_data = schemas.QuizSubmit(
    identifier=1,
    questions=[
        schemas.QuestionSubmit(
            identifier=1,
            answers=[
                schemas.AnswerSubmit(identifier=1, is_correct=True),
                schemas.AnswerSubmit(identifier=2, is_correct=True),
                schemas.AnswerSubmit(identifier=3, is_correct=True),
            ]
        )
    ]
)

submit4_data = schemas.QuizSubmit(
    identifier=1,
    questions=[
        schemas.QuestionSubmit(
            identifier=1,
            answers=[
                schemas.AnswerSubmit(identifier=1, is_correct=True),
                schemas.AnswerSubmit(identifier=2, is_correct=True),
                schemas.AnswerSubmit(identifier=3, is_correct=True),
                schemas.AnswerSubmit(identifier=4, is_correct=True)
            ]
        )
    ]
)

validation_result1_data = schemas.QuizValidationResult(total_points=3, points=3)
validation_result2_data = schemas.QuizValidationResult(total_points=3, points=1)
validation_result3_data = None
validation_result4_data = schemas.QuizValidationResult(total_points=3, points=0)


class TestServices(unittest.TestCase):

    @parameterized.expand([
        [quiz_data, submit1_data, validation_result1_data],
        [quiz_data, submit2_data, validation_result2_data],
        [quiz_data, submit3_data, validation_result3_data],
        [quiz_data, submit4_data, validation_result4_data]
    ])
    def test_validate_quiz(self,
                           quiz: schemas.Quiz,
                           quiz_submit: schemas.QuizSubmit,
                           check_validation_result: schemas.QuizValidationResult):
        validation_result = services.validate_quiz(quiz, quiz_submit)
        assert validation_result == check_validation_result
