from app.database import pool

def cleanup_products():
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                DELETE FROM app.product_search
                WHERE created_at < NOW() - INTERVAL '2 hours';
            """)
            conn.commit()
    print("INFO:\tExpired products cleaned up.")



