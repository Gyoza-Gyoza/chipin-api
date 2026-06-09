from fastapi import APIRouter
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

@router.post("/create_user")
def create_user(user: User):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO users
    (username, password, email, first_name, last_name)
    VALUES (%s, %s, %s, %s, %s)""",
                   (user.username, user.password, user.email, user.first_name, user.last_name))

    conn.commit()
    conn.close()
    return {f"message": f"{user.username} created successfully"}

@router.get("/users")
def get_users():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT username, password, email, first_name, last_name FROM users""")

    users = cursor.fetchall()
    conn.close()
    return users

@router.get("/users/{user_id}")
def get_user(user_id: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT username, password, email, first_name, last_name FROM users WHERE user_id = %(id)s""", {'id': user_id})
    user = cursor.fetchone()

    conn.close()
    return user

@router.put("/update_user/{user_id}")
def update_user(user_id: int, user: User):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE users WHERE user_id = %s""", user_id)

    cursor.commit()
    conn.close()

    return {f"message": f"{user.username} updated successfully"}

@router.delete("/delete_uesr/{user_id}")
def delete_user(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    DELETE FROM users WHERE user_id = %s""", user_id)

    cursor.commit()
    conn.close()
    return {"message": f"{user_id} deleted successfully"}