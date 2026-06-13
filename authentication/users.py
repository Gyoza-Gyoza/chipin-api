from fastapi import APIRouter,status,HTTPException
from pydantic import BaseModel
from database import get_connection
from argon2 import PasswordHasher
from psycopg.errors import UniqueViolation

class User(BaseModel):
    username: str
    password: str
    email: str
    first_name: str
    last_name: str
    phone_number: int

router = APIRouter(
    prefix = "/users",
    tags = ["Users"]
)

passwordHasher = PasswordHasher()
@router.post(
    "/",
status_code = status.HTTP_201_CREATED
)
def create_user(user: User):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        hashedPassword = passwordHasher.hash(user.password)

        cursor.execute("""
        INSERT INTO users
        (username, password, email, first_name, last_name, phone_number)
        VALUES (%s, %s, %s, %s, %s, %s)""",
                       (user.username, hashedPassword, user.email, user.first_name, user.last_name, user.phone_number))

        conn.commit()
        cursor.close()
        conn.close()
        return {f"message": f"{user.username} created successfully"}

    except UniqueViolation:
        conn.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,)

@router.get(
    "/",
    status_code = status.HTTP_200_OK
)
def get_users():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT username, password, email, first_name, last_name FROM users""")

    users = cursor.fetchall()
    if users is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No users found")

    cursor.close()
    conn.close()
    return users

@router.get(
    "/{user_id}",
status_code = status.HTTP_200_OK
)
def get_user(user_id: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT username, password, email, first_name, last_name, phone_number FROM users WHERE user_id = %(id)s""", {'id': user_id})

    user = cursor.fetchone()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No user found")
    cursor.close()
    conn.close()
    return user

@router.put(
    "/{user_id}",
status_code = status.HTTP_200_OK
)
def update_user(user_id: str, user: User):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE users set username= %(username)s, 
    password= %(password)s, 
    email= %(email)s, 
    first_name= %(first_name)s, 
    last_name= %(last_name)s, 
    phone_number = %(phone_number)s
    WHERE user_id = %(id)s""",
                   {'id': user_id,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'username': user.username,
                    'password': user.password,
                    'phone_number': user.phone_number})

    conn.commit()
    cursor.close()
    conn.close()

    return {f"message": f"{user.username} updated successfully"}

@router.delete(
    "/{user_id}",
    status_code = status.HTTP_204_NO_CONTENT
)
def delete_user(user_id: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    DELETE FROM users WHERE user_id = %(id)s""", {'id': user_id})

    conn.commit()
    cursor.close()
    conn.close()
    return {"message": f"{user_id} deleted successfully"}