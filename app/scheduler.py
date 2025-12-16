from datetime import datetime, timedelta
from app.database import SessionLocal
from app.models import Question, Status
import asyncio
from app.websocket import broadcast

def escalate_questions():
    db = SessionLocal()
    threshold = datetime.now() - timedelta(minutes=5)

    questions = db.query(Question).filter(
        Question.status == Status.PENDING,
        Question.created_at <= threshold
    ).all()

    updated_ids = []

    for q in questions:
        if q.status != Status.ANSWERED:
            q.status = Status.ESCALATED
        updated_ids.append(q.id)

    db.commit()
    db.close()

    if updated_ids:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(
            broadcast({
                "event": "ESCALATED",
                "ids": updated_ids
            })
        )
        loop.close()
