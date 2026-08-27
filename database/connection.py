from __future__ import annotations
import os
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row

load_dotenv()

def connection_string() -> str:
    return os.getenv("DATABASE_URL", "postgresql://{user}:{password}@{host}:{port}/{db}").format(
        user=os.getenv("POSTGRES_USER", "knowledge_app"), password=os.getenv("POSTGRES_PASSWORD", ""),
        host=os.getenv("POSTGRES_HOST", "127.0.0.1").replace("localhost", "127.0.0.1"), port=os.getenv("POSTGRES_PORT", "5432"),
        db=os.getenv("POSTGRES_DB", "knowledge"))

def connect() -> psycopg.Connection:
    return psycopg.connect(connection_string(), row_factory=dict_row)
