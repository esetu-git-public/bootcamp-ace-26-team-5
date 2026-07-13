import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

db_path = BASE_DIR / "claims.db"
schema_path = BASE_DIR / "schema_sqlite.sql"

connection = sqlite3.connect(db_path)

with open(schema_path, "r", encoding="utf-8") as file:
    schema_sql = file.read()

connection.executescript(schema_sql)

connection.close()

print("Database initialized successfully.")
print(f"Database file: {db_path}")