from fastapi import APIRouter, status
from pydantic import BaseModel
from database import get_connection

router = APIRouter(
    prefix="/authentication",
    tags=["Authentication"]
)

class User(BaseModel):
    username: str
    password: str
    email: str
    first_name: str
    last_name: str

@router.post(
    "/users",
        status_code=status.HTTP_201_CREATED
)
def create_user(user: User):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
            INSERT INTO users
            (username, password, email, first_name, last_name)
            VALUES (%s, %s, %s, %s, %s)""",
                           (user.username, user.password, user.email, user.first_name, user.last_name))

            return {f"message": f"{user.username} created successfully"}

@router.get(
    "/users",
    status_code=status.HTTP_200_OK
)
def get_users():
    with get_connection() as conn:
        with conn.cursor as cursor:
            cursor.execute("""
            SELECT username, password, email, first_name, last_name FROM users""")

            users = cursor.fetchall()
            return users

@router.get("/users/{user_id}")
def get_user(user_id: str):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
            SELECT username, password, email, first_name, last_name FROM users WHERE user_id = %(id)s""", {'id': user_id})
            user = cursor.fetchone()

            return user

@router.put("/user/{user_id}")
def update_user(user_id: str, user: User):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
            UPDATE users set username= %(username)s, 
            password= %(password)s, 
            email= %(email)s, 
            first_name= %(first_name)s, 
            last_name= %(last_name)s
            WHERE user_id = %(id)s""",
                           {'id': user_id,
                            'first_name': user.first_name,
                            'last_name': user.last_name,
                            'email': user.email,
                            'username': user.username,
                            'password': user.password})

            return {f"message": f"{user.username} updated successfully"}

@router.delete("/user/{user_id}")
def delete_user(user_id: str):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
            DELETE FROM users WHERE user_id = %(id)s""", {'id': user_id})

            conn.commit()
            return {"message": f"{user_id} deleted successfully"}