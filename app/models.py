from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base
import enum

class Status(enum.Enum):
    PENDING = "PENDING"
    ESCALATED = "ESCALATED"
    ANSWERED = "ANSWERED"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    token = Column(String, nullable=True)
    role = Column(String, default="ADMIN") 

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True)
    message = Column(String, nullable=False)
    status = Column(Enum(Status), default=Status.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)

    answers = relationship("Answer", back_populates="question")


class Answer(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True)
    answer = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    question_id = Column(Integer, ForeignKey("questions.id"))
    question = relationship("Question", back_populates="answers")
