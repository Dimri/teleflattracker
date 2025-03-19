import json
import math
import sqlite3

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# manage database connection
def get_db():
    conn = sqlite3.connect("telegram_data.db")
    try:
        yield conn
    finally:
        conn.close()


def sanitize_floats(value):
    if isinstance(value, float):
        if not math.isfinite(value):
            return False
    return True


@app.get("/messages")
def get_messages(db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM message_data;")
    messages = [
        {
            "id": row[0],
            "raw_text": row[1],
            "time_created": row[2],
            "author": row[3],
            "details": json.loads(row[4]),
        }
        for row in cursor.fetchall()
    ]
    for msg in messages:
        print(msg["details"])
    messages = [msg for msg in messages if sanitize_floats(msg["details"]["BHK"])]
    print(f"Returning object with length: {len(messages)}")
    return messages
