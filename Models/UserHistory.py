from datetime import datetime

class UserHistory:
    # This class represents an AnswerTag object, which stores information about a specific tag associated with an answer.
    def __init__(self, id: int, question_id: int, question: str, assignment_id: int, answer_id: int, answer_score: int, tag_prompt_deployment_id: int, user_id: int, 
                value: str, created_at: datetime, updated_at: datetime, tag_prompt_id: None, comments: str, prompt: str) -> None:
        self.id = id
        self.question_id = question_id
        self.question = question
        self.assignment_id = assignment_id # - assignment_id: an integer representing the ID of the assignment associated with this AnswerTag
        self.answer_id = answer_id # - answer_id: an integer representing the ID of the answer associated with this AnswerTag
        self.answer_score = answer_score
        self.tag_prompt_deployment_id = tag_prompt_deployment_id # - tag_prompt_deployment_id: an integer representing the ID of the tag prompt deployment associated with this AnswerTag
        self.user_id = user_id # - user_id: an integer representing the ID of the user associated with this AnswerTag
        self.value = value # It represents the values of the ANSWER TAGS i.e. yes - 1, N0 - -1, None and 0
        self.created_at = created_at #.strftime('%Y-%m-%d %H:%M:%S') 
        self.updated_at = updated_at
        self.tag_prompt_id = tag_prompt_id # - tag_prompt_id: an integer representing the ID of the tag prompt associated with this AnswerTag
        self.comments = comments
        self.prompt = prompt