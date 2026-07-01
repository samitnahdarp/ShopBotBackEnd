
import uuid
from app.database import pool

def validate_session(session_id: str):
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT * FROM app.session
                WHERE session_id = %s;
            """, (session_id,))
            session = cur.fetchone()
            if session is None:
                return False
            return True

def get_session() -> str:
    with pool.connection() as conn:
        with conn.cursor() as cur:
            while True:
                new_session_id = str(uuid.uuid4())
                cur.execute(
                    "SELECT session_id FROM app.session WHERE session_id = %s",
                    (new_session_id,)
                )
                if not cur.fetchone():
                    break
            return new_session_id
    