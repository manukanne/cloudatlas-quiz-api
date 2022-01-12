from schemas import Quiz, QuizSubmit, QuestionSubmit, AnswerSubmit, QuizValidationResult


def validate_quiz(quiz: Quiz, quiz_submit: QuizSubmit) -> [QuizValidationResult, None]:
    """
    Validates a quiz and returns the total and reached points.
    If one answer is incorrect, the user gets 0 reached points, this is to prevent that a user checks all answers
    :param quiz: The quiz data
    :param quiz_submit: The submitted quit data
    :return: Validation result, contains the total and the reached points
    """
    try:
        total_points, points = 0, 0
        for question in quiz.questions:
            total_points += sum([1 for x in question.answers if x.is_correct])
            question_submit: QuestionSubmit = [x for x in quiz_submit.questions if question.identifier == x.identifier][
                0]
            for answer in question.answers:
                answer_submit: AnswerSubmit = [x for x in question_submit.answers if answer.identifier == x.identifier][
                    0]
                # If an answer is checked which is not correct, give 0 points
                if answer_submit.is_correct and not answer.is_correct:
                    return QuizValidationResult(total_points=total_points, points=0)

                points += 1 if answer.is_correct and answer_submit.is_correct else 0
        return QuizValidationResult(total_points=total_points, points=points)
    except IndexError:
        return None
