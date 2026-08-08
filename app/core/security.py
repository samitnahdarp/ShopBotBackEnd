

import uuid

from fastapi import HTTPException
from app.database import pool

def validate_session(session_id: str):
    try:
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT * FROM app.active_session
                    WHERE session_id = %s;
                """, (session_id,))
                session = cur.fetchone()
                if session is None:
                    return False
                return True
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid session ID")

def get_session() -> str:
    with pool.connection() as conn:
        with conn.cursor() as cur:
            while True:
                new_session_id = str(uuid.uuid4())
                cur.execute(
                    "SELECT session_id FROM app.active_session WHERE session_id = %s",
                    (new_session_id,)
                )
                if not cur.fetchone():
                    break
            return new_session_id
    