from pydantic import BaseModel
from datetime import datetime
from typing import List

class QuestionCreate(BaseModel):
    message: str

class AnswerCreate(BaseModel):
    answer: str

class AnswerResponse(BaseModel):
    id: int
    answer: str
    created_at: datetime

    class Config:
        orm_mode = True

class QuestionResponse(BaseModel):
    id: int
    message: str
    status: str
    created_at: datetime
    answers: List[AnswerResponse] = []

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    role: str
    userId: int
    username: str

