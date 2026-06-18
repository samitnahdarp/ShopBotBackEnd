import psycopg
from app.core.settings import settings
from contextlib import closing

def create_schema():
    conn = None
    try:
        conn = psycopg.connect(
            dbname=settings.db_name,
            user=settings.db_user,
            password=settings.db_password,
            host=settings.db_host,
            port=settings.db_port,
        )

        with conn.cursor() as cur:
            cur.execute("""
            SET search_path TO app;
            CREATE TABLE IF NOT EXISTS profile (
                user_id SERIAL PRIMARY KEY,
                last_accessed TIMESTAMP DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS website (
                website_id SERIAL PRIMARY KEY,
                website_name VARCHAR(255) NOT NULL,
                website_url VARCHAR(255) NOT NULL
            );

            CREATE TABLE IF NOT EXISTS product_search (
                product_search_id SERIAL PRIMARY KEY,
                searched_product_name VARCHAR(255) NOT NULL UNIQUE,
                last_searched TIMESTAMP DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS search_queue (
                search_queue_id SERIAL PRIMARY KEY,
                product_search_id INT NOT NULL REFERENCES product_search(product_search_id) ON DELETE CASCADE,
                website_id INT NOT NULL REFERENCES website(website_id),
                status_code SMALLINT NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW(),
                error_message TEXT,
                UNIQUE(product_search_id, website_id)
            );

            CREATE TABLE IF NOT EXISTS user_search (
                user_id INT NOT NULL REFERENCES profile(user_id) ON DELETE CASCADE,
                product_search_id INT NOT NULL REFERENCES product_search(product_search_id) ON DELETE CASCADE,
                website_id INT NOT NULL REFERENCES website(website_id),
                PRIMARY KEY(user_id, product_search_id, website_id)
            );

            CREATE TABLE IF NOT EXISTS scraped_product (
                scraped_product_id SERIAL PRIMARY KEY,
                product_search_id INT NOT NULL REFERENCES product_search(product_search_id) ON DELETE CASCADE,
                website_id INT NOT NULL REFERENCES website(website_id),
                name VARCHAR(255),
                rating FLOAT,
                price NUMERIC(10,2),
                description TEXT,
                link TEXT,
                image TEXT
            );"""
            );
            conn.commit()

    except psycopg.OperationalError as e:
        print("Database connection failed:", e)

    finally:
        if conn is not None:
            conn.close()
        
