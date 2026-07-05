import sqlite3
from pathlib import Path

db_path = Path(__file__).resolve().parent / "claims.db"

connection = sqlite3.connect(db_path)
cursor = connection.cursor()

cursor.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type='table'
    ORDER BY name;
""")

tables = cursor.fetchall()

print("Tables created:")
for table in tables:
    print("-", table[0])

connection.close()