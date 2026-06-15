from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from database import get_connection
from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, VerifyMismatchError


class LoginRequest(BaseModel):
    username: str
    password: str

router = APIRouter(
    prefix = '/login',
    tags = ['Login']
)

passwordHasher = PasswordHasher()

@router.post('/')
def login(request: LoginRequest):
    conn = get_connection()
    cursor = conn.cursor()

    print(request)
    cursor.execute("""
    SELECT password FROM users 
    WHERE username = %s""",
                        (request.username,))

    storedPassword = cursor.fetchone()

    try:
        passwordHasher.verify(storedPassword['password'], request.password)

    except VerifyMismatchError:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED,
                            detail = "Incorrect credentials")
    return {"message": "Login successful"}