import time
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field, field_validator
import bcrypt
import uuid

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

        # Create new user entry 
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
        
        # Add user entry to user_current_portfolio (default is NULL)
        connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO user_current_portfolio (user_id)
                VALUES (:user_id)
                """
            ),
            {"user_id": created.id}
        )

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
    session_token: str

@router.post("/login", response_model=LoginResponse)
def login(login_info: UserLogin):
    """
    Validates a user's login information, returns the salted password hash 
    to use for accessing account's portfolios, buying, and selling
    """

    with db.engine.begin() as connection:
        user = connection.execute(
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
        if not user or not bcrypt.checkpw(login_info.password.encode(), user.password_hash.encode()):
            raise HTTPException(status_code=401, detail="Invalid username or password")

        # Generate temporary token & insert into temp_user_tokens table
        token = str(uuid.uuid4())
        connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO temp_user_tokens (token, user_id) 
                VALUES (:token, :user_id)
                """
            ),
            {
                "token": token,
                "user_id": user.id
            }
        )

        # Successful login 
        return LoginResponse(
            message="Credentials verified",
            user_id=user.id,
            username=user.username,
            session_token=token
        )


class UserLogout(BaseModel):
    username: str 
    session_token: str

class LogoutResponse(BaseModel):
    message: str
    user_id: int
    username: str
    session_token: str

@router.post("/logout", response_model=LogoutResponse)
def logout(logout_info: UserLogout):
    """
    Logs user out by deleting their session token
    """

    with db.engine.begin() as connection:
        res = connection.execute(
            sqlalchemy.text(
                """
                DELETE FROM temp_user_tokens
                WHERE token = :token AND user_id = (
                    SELECT id FROM users WHERE username = :username
                )
                RETURNING token, user_id
                """
            ),
            {
                "username": logout_info.username,
                "token": logout_info.session_token
            }
        ).first()

        # Checks if session exists
        if not res:
            raise HTTPException(status_code=404, detail="Session not found or already logged out")

        # Successful logout
        return LogoutResponse(
            message="Successfully logged out",
            user_id=res.user_id,
            username=logout_info.username,
            session_token=res.token
        )
