from fastapi import APIRouter,status,HTTPException
from pydantic import BaseModel
from data.database import get_connection
from argon2 import PasswordHasher
from psycopg.errors import UniqueViolation

class User(BaseModel):
    username: str
    password: str
    email: str
    first_name: str
    last_name: str
    phone_number: str

class UserDetails(BaseModel):
    user_id: int
    username: str
    email: str
    first_name: str
    last_name: str
    phone_number: str

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
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING user_id""",
                       (user.username, hashedPassword, user.email, user.first_name, user.last_name, user.phone_number))
        user_id = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        return user_id

    except UniqueViolation:
        conn.rollback()
        raise HTTPException(status_code = status.HTTP_409_CONFLICT,)

@router.get(
    "/",
    status_code = status.HTTP_200_OK,
    response_model = list[User]
)
def get_users():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT username, password, email, first_name, last_name, phone_number FROM users""")

    users = cursor.fetchall()
    if users is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail = "No users found")
    user_list = []
    for user in users:
        user_list.append(User(username=user['username'],
                              password=user['password'],
                              email=user['email'],
                              first_name=user['first_name'],
                              last_name=user['last_name'],
                              phone_number=user['phone_number']))
    cursor.close()
    conn.close()
    return user_list

@router.get(
    "/{username}",
    status_code = status.HTTP_200_OK,
    response_model = UserDetails
)
def get_user(username: str):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
        SELECT user_id, email, first_name, last_name, phone_number FROM users
        WHERE username = %s""",
                       (username,))

        user = cursor.fetchone()

        return (UserDetails(username = username,
                            user_id = user['user_id'],
                            email = user['email'],
                            first_name = user['first_name'],
                            last_name = user['last_name'],
                            phone_number = user['phone_number']))

    except TypeError:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail = "User not found")

    except Exception as e:
        print(type(e))
        print(e)

    finally:
        cursor.close()
        conn.close()

@router.get(
    "/id/{user_id}",
    status_code = status.HTTP_200_OK,
    response_model = UserDetails
)
def get_user_by_id(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
        SELECT username, email, first_name, last_name, phone_number FROM users
        WHERE user_id = %s""",
                       (user_id,))

        user = cursor.fetchone()

        return (UserDetails(username = user['username'],
                            user_id = user_id,
                            email = user['email'],
                            first_name = user['first_name'],
                            last_name = user['last_name'],
                            phone_number = user['phone_number']))

    except TypeError:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail = "User not found")

    except Exception as e:
        print(type(e))
        print(e)

    finally:
        cursor.close()
        conn.close()

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