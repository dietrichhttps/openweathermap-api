import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
import config


def get_connection():
    return psycopg2.connect(config.DATABASE_URL)


@contextmanager
def get_db_cursor():
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        yield cursor
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def create_tables():
    with get_db_cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS requests (
                id SERIAL PRIMARY KEY,
                city VARCHAR(100) NOT NULL,
                request_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR(20) NOT NULL,
                error_message TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS responses (
                id SERIAL PRIMARY KEY,
                request_id INTEGER NOT NULL REFERENCES requests(id) ON DELETE CASCADE,
                temperature REAL,
                feels_like REAL,
                humidity INTEGER,
                pressure INTEGER,
                wind_speed REAL,
                description VARCHAR(255),
                response_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_requests_request_time ON requests(request_time)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_responses_request_id ON responses(request_id)
        """)
