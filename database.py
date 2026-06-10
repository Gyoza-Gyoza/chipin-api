import psycopg
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv()
print("PASSWORD:", repr(os.getenv("DATABASE_PASSWORD")))
print("HOST:", repr(os.getenv("DATABASE_HOST")))
print("PORT:", repr(os.getenv("DATABASE_PORT")))
print(list(os.environ.keys()))
def get_connection():
    conn = psycopg.connect(
        dbname="chipin-db",
        user="postgres",
        password=os.getenv("DATABASE_PASSWORD"),
        host=os.getenv("DATABASE_HOST"),
        port=os.getenv("DATABASE_PORT")
    )
    return conn