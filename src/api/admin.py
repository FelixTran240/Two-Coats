from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database import SessionLocal
from src.api.models import User
from src.api import auth

router = APIRouter(
    tags=["stocks"],
    dependencies=[Depends(auth.get_api_key)],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/reset_user")
def reset_user(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(username=username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": f"User '{username}' has been reset (deleted)."}
