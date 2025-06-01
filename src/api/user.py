import time
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field, field_validator
import bcrypt

import sqlalchemy
from src.api import auth
from src import database as db


router = APIRouter(
    tags=["users"],
    dependencies=[Depends(auth.get_api_key)],
)


class UserCreate(BaseModel):
    username: str
    password: str

class CreateUserResponse(BaseModel):
    message: str
    id: int
    username: str 


@router.post("/create", response_model=CreateUserResponse)
def create_user(new_user: UserCreate):
    """
    Creates a new user with a hashed password (bcrypt hashing algorithm)
    """
    
    with db.engine.begin() as connection:
        # Check for existing user
        res = connection.execute(
            sqlalchemy.text(
                """
                SELECT id
                FROM users
                WHERE username = :username
                """
            ),
            {"username": new_user.username}
        ).first()

        if res:
            raise HTTPException(status_code=400, detail="Username is taken")

        # Generate hash
        hashed_pw = bcrypt.hashpw(new_user.password.encode(), bcrypt.gensalt()).decode() 

        # Create new user entry & return result
        created = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO users (username, password_hash)
                VALUES (:username, :password_hash)
                RETURNING id, username
                """
            ),
            {
                "username": new_user.username,
                "password_hash": hashed_pw, 
            }
        ).one()

        # Success response
        return CreateUserResponse(
            message="User successfully created", 
            id=created.id,
            username=created.username
        ) 


class UserLogin(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    message: str
    user_id: int
    username: str

@router.post("/login", response_model=LoginResponse)
def login(login_info: UserLogin):
    """
    Validates a login attempt 
    """

    with db.engine.begin() as connection:
        res = connection.execute(
            sqlalchemy.text(
                """
                SELECT id, username, password_hash
                FROM users
                WHERE username = :username 
                """
            ),
            {"username": login_info.username}
        ).first()

        # Check if user exists, then compares password hashes
        if not res or not bcrypt.checkpw(login_info.password.encode(), res.password_hash.encode()):
            raise HTTPException(status_code=401, detail="Invalid username or password")

        # Success response 
        return LoginResponse(
            message="Login successful",
            user_id=res.id,
            username=login_info.username
        )
