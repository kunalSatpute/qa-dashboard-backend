from fastapi import FastAPI, WebSocket
from app.websocket import connect, disconnect
from app.database import Base, engine
from app.routes import questions
from fastapi.middleware.cors import CORSMiddleware

from apscheduler.schedulers.background import BackgroundScheduler
from app.scheduler import escalate_questions

from app.routes import questions, userlogin


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Q&A Dashboard")
app.include_router(questions.router)

# ✅ CORS CONFIG (VERY IMPORTANT)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await connect(ws)
    try:
        while True:
            await ws.receive_text()  # keep alive
    except:
        disconnect(ws)

app.include_router(userlogin.router)
app.include_router(questions.router)

scheduler = BackgroundScheduler()
scheduler.add_job(escalate_questions, "interval", minutes=1)
scheduler.start()
