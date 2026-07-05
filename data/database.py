import psycopg
from psycopg.rows import dict_row
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv()

def get_connection(dbname:str = "chipin-db"):
    conn = psycopg.connect(
        dbname=dbname,
        user="postgres",
        password=os.getenv("DATABASE_PASSWORD"),
        host=os.getenv("DATABASE_HOST"),
        port=os.getenv("DATABASE_PORT"),
        row_factory=dict_row
    )
    return conn