from datetime import datetime

class AnswerTag:
    def __init__(self, id: int, assignment_id: int, answer_id: int, tag_prompt_deployment_id: int, user_id: int, 
                value: str, created_at: datetime, updated_at: datetime) -> None:
        self.id = id
        self.assignment_id = assignment_id
        self.answer_id = answer_id
        self.tag_prompt_deployment_id = tag_prompt_deployment_id
        self.user_id = user_id
        self.value = value
        self.created_at = created_at #.strftime('%Y-%m-%d %H:%M:%S') 
        self.updated_at = updated_at
        