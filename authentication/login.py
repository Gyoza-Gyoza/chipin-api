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

    try:
        cursor.execute("""
            SELECT password FROM users 
            WHERE username = %s""",
                       (request.username,))

        user = cursor.fetchone()

        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Incorrect credentials")
        else:
            passwordHasher.verify(user['password'], request.password)

    except VerifyMismatchError:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED,
                            detail = "Incorrect credentials")
    except Exception as e:
        print(type(e))
        print(e)
        raise

    finally:
        cursor.close()
        conn.close()

    return {"message": "Login successful"}