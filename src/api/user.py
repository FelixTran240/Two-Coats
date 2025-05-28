import time
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from src.database import SessionLocal
from src.api.models import User

router = APIRouter()

class UserCreate(BaseModel):
    name: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/user")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter_by(username=user.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    # holdings and balance will be implemented later
    new_user = User(username=user.name)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"username": new_user.username}

@router.get("/user")
def get_user(name: str, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(username=name).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"username": user.username}