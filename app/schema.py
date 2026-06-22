import psycopg
from core.settings import settings

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

------------------------------------------------------------
-- PROFILE TABLE
------------------------------------------------------------
CREATE TABLE IF NOT EXISTS profile (
    id UUID PRIMARY KEY,
    created_at TIMESTAMP DEFAULT NOW(),
    last_accessed TIMESTAMP DEFAULT NOW()
);

------------------------------------------------------------
-- PRODUCT SEARCH TABLE
------------------------------------------------------------
CREATE TABLE IF NOT EXISTS product_search (
    product_search_id SERIAL PRIMARY KEY,
    searched_product_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    last_searched TIMESTAMP DEFAULT NOW()
);

------------------------------------------------------------
-- USER SEARCH TABLE
------------------------------------------------------------
CREATE TABLE IF NOT EXISTS user_search (
    user_id UUID NOT NULL REFERENCES profile(id) ON DELETE CASCADE,
    product_search_id INT NOT NULL REFERENCES product_search(product_search_id) ON DELETE CASCADE,
    PRIMARY KEY(user_id, product_search_id)
);

------------------------------------------------------------
-- SCRAPED PRODUCT TABLE
------------------------------------------------------------
CREATE TABLE IF NOT EXISTS scraped_product (
    scraped_product_id SERIAL PRIMARY KEY,
    product_search_id INT NOT NULL REFERENCES product_search(product_search_id) ON DELETE CASCADE,
    name VARCHAR(255),
    rating FLOAT,
    price NUMERIC(10,2),
    description TEXT,
    link TEXT,
    image TEXT
);

------------------------------------------------------------
-- SEARCH QUEUE TABLE (MISSING BEFORE)
------------------------------------------------------------
CREATE TABLE IF NOT EXISTS search_queue (
    id SERIAL PRIMARY KEY,
    product_search_id INT REFERENCES product_search(product_search_id),
    created_at TIMESTAMP DEFAULT NOW()
);

------------------------------------------------------------
-- FUNCTION: update last_accessed
------------------------------------------------------------
CREATE OR REPLACE FUNCTION update_last_access()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_accessed = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

------------------------------------------------------------
-- TRIGGER: update last_accessed on profile update
------------------------------------------------------------
DROP TRIGGER IF EXISTS set_last_accessed ON profile;

CREATE TRIGGER set_last_accessed
BEFORE UPDATE ON profile
FOR EACH ROW
EXECUTE FUNCTION update_last_access();


"""
            );
            conn.commit()

    except psycopg.OperationalError as e:
        print("Database connection failed:", e)

    finally:
        if conn is not None:
            conn.close()
        
create_schema();