import os
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL no configurada.")


def init_db():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS pacientes (
                    id                SERIAL PRIMARY KEY,
                    nombre            TEXT NOT NULL,
                    apellido          TEXT NOT NULL,
                    telefono          TEXT,
                    fecha_nacimiento  DATE,
                    historia_clinica  TEXT,
                    activo_sn         BOOLEAN NOT NULL DEFAULT TRUE,
                    dia_ultima_sesion DATE,
                    created_at        TIMESTAMP NOT NULL DEFAULT NOW(),
                    updated_at        TIMESTAMP NOT NULL DEFAULT NOW()
                )
            """)


@contextmanager
def get_connection():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
