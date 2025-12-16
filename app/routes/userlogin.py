from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User
from app.auth import create_token
from app.schemas import (TokenResponse, UserLogin)

router = APIRouter(prefix="/auth", tags=["Auth"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register")
def register(username: str, password: str, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(400, "User already exists")

    user = User(
        username=username,
        password=password,
        role="ADMIN"
    )
    db.add(user)
    db.commit()
    return {"message": "Admin registered"}

@router.post("/login", response_model=TokenResponse)
def login(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user or password != user.password:
        raise HTTPException(401, "Invalid credentials")

    token = create_token(user.id, user.role)
    user.token = token
    db.commit()

    return {"access_token": token, "userId": user.id, "role": user.role, "username": user.username}

@router.get("/logout")
def logout(userId: int, db: Session = Depends(get_db)):

    user = db.query(User).filter(userId != None).first()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    user.token = None
    db.commit()

    return {"message": "Logged out successfully"}
