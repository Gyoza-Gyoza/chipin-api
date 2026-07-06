import psycopg
from psycopg.rows import dict_row
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv()

def get_connection():
    conn = psycopg.connect(
        dbname=os.getenv("DATABASE_NAME"),
        user=os.getenv("DATABASE_USER"),
        password=os.getenv("DATABASE_PASSWORD"),
        host=os.getenv("DATABASE_HOST"),
        port=os.getenv("DATABASE_PORT"),
        row_factory=dict_row
    )
    return conn