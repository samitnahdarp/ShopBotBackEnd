from app.core.settings import settings
from app.database import pool

def create_schema():
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                        DROP SCHEMA IF EXISTS app CASCADE;

                        CREATE SCHEMA IF NOT EXISTS app;
                        
                        SET search_path TO app;

                        ------------------------------------------------------------
                        -- HANDLING sessions
                        ------------------------------------------------------------
                        CREATE UNLOGGED TABLE IF NOT EXISTS session (
                            session_id UUID PRIMARY KEY,
                            username VARCHAR(255) NOT NULL,
                            created_at TIMESTAMP DEFAULT NOW()
                        );      

                        ------------------------------------------------------------
                        -- PROFILE TABLE
                        ------------------------------------------------------------
                        CREATE TABLE IF NOT EXISTS profile (
                            user_id SERIAL PRIMARY KEY,
                            username VARCHAR(255) UNIQUE NOT NULL,
                            password_hash CHAR(60) NOT NULL,
                            created_at TIMESTAMP DEFAULT NOW()
                        );

                        ------------------------------------------------------------
                        -- PRODUCT SEARCH TABLE
                        ------------------------------------------------------------
                        CREATE TABLE IF NOT EXISTS product_search (
                            product_search_id SERIAL PRIMARY KEY,
                            searched_product_name VARCHAR(255) NOT NULL,
                            created_at TIMESTAMP DEFAULT NOW()
                        );

                        ------------------------------------------------------------
                        -- SCRAPED PRODUCT TABLE
                        ------------------------------------------------------------
                        CREATE TABLE IF NOT EXISTS scraped_product (
                            scraped_product_id SERIAL PRIMARY KEY,
                            product_search_id INT NOT NULL REFERENCES product_search(product_search_id) ON DELETE CASCADE,
                            page_number INT NOT NULL,
                            filters VARCHAR(50) NOT NULL,
                            name VARCHAR(255),
                            rating FLOAT,
                            price NUMERIC(10,2),
                            description TEXT,
                            link TEXT,
                            image TEXT
                        );

                        """
                );
            conn.commit()