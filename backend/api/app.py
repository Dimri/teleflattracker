from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import json

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
    print(messages[0])
    print(f"Returning object with length: {len(messages)}")
    return messages
