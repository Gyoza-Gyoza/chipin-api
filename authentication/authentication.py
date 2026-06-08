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