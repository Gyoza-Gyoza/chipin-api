import psycopg
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    conn = psycopg.connect(
        database="chipin-db",
        user="postgres",
        password=os.getenv("DATABASE_PASSWORD"),
        host=os.getenv("DATABASE_HOST"),
        port=os.getenv("DATABASE_PORT")
    )
    return conn