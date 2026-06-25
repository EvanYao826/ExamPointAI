from pydantic import BaseModel, Field


class OptionItem(BaseModel):
    id: int
    option_key: str
    content: str

    class Config:
        from_attributes = True


class QuestionResponse(BaseModel):
    id: int
    bank_id: int
    type: str
    content: str
    difficulty: int
    options: list[OptionItem] = []


class SubmitRequest(BaseModel):
    question_id: int = Field(..., description="题目ID")
    user_answer: str = Field(..., description="用户答案")
    cost_time: int = Field(default=0, description="耗时秒数")


class SubmitResponse(BaseModel):
    is_correct: bool
    correct_answer: str
    analysis: str
