from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.websocket import broadcast
from sqlalchemy import case, desc
from app.auth import get_current_admin
from app.models import Question, Status, Answer
from app.schemas import (
    QuestionCreate,
    QuestionResponse,
    AnswerCreate,
    AnswerResponse,
)
from typing import List

router = APIRouter(prefix="/questions", tags=["Questions"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 1️⃣ Submit Question (Guest)
@router.post("/submitQuestion", response_model=QuestionResponse)
async def create_question(q: QuestionCreate, db: Session = Depends(get_db)):
    if not q.message.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    question = Question(message=q.message)
    db.add(question)
    db.commit()
    db.refresh(question)

    await broadcast({
        "event": "NEW_QUESTION",
        "question": question.id
    })

    return question


# 2️⃣ Get All Questions (Forum)
@router.get("/getAllQuestions", response_model=List[QuestionResponse])
def get_questions(db: Session = Depends(get_db)):
    return (
        db.query(Question)
        .order_by(
            case(
                (Question.status == Status.ESCALATED, 0),
                else_=1
            ),
            desc(Question.created_at)
        )
        .all()
    )


# 3️⃣ Answer a Question (Admin / User)
@router.post("/{id}/answer", response_model=AnswerResponse)
async def answer_question(
    id: int,
    payload: AnswerCreate,
    db: Session = Depends(get_db)
):
    question = db.query(Question).filter(Question.id == id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    if not payload.answer.strip():
        raise HTTPException(status_code=400, detail="Answer cannot be empty")

    answer = Answer(answer=payload.answer, question_id=id)
    db.add(answer)
    db.commit()
    db.refresh(answer)

    await broadcast({
        "event": "NEW_ANSWER",
        "question_id": id,
        "answer": payload.answer
    })
    
    return answer


# 4️⃣ Explicitly Mark as Answered (Admin only – optional)
@router.put("/{id}/mark-answered", dependencies=[Depends(get_current_admin)])
async def mark_answered(id: int, db: Session = Depends(get_db)):
    question = db.query(Question).filter(Question.id == id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    question.status = Status.ANSWERED
    db.commit()

    await broadcast({
        "event": "ANSWERED",
        "question_id": id
    })

    return {"message": "Question marked as answered"}
