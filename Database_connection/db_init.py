import psycopg2
from psycopg2 import sql
import logging
import os

# Database configuration
DB_NAME = "mlops_image_db"
DB_USER = "postgres"
DB_PASSWORD = "admin"
DB_PORT = "5432"
DB_HOST = "postgres"

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def create_database(db_name=DB_NAME):
    """Creates the PostgreSQL database if it does not exist."""
    try:
        conn = psycopg2.connect(
            database='postgres',
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute(f"SELECT 1 FROM pg_database WHERE datname='{db_name}';")
        if not cur.fetchone():
            cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))
            logging.info(f"[DB] Database '{db_name}' created.")
        else:
            logging.info(f"[DB] Database '{db_name}' already exists.")
        cur.close()
        conn.close()
    except Exception as e:
        logging.error(f"[DB ERROR] Database creation failed: {e}")
        raise e


def create_table(db_name, table_name):
    """Creates the required table with image and label columns."""
    try:
        conn = psycopg2.connect(
            database=db_name,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cur = conn.cursor()
        cur.execute(sql.SQL(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id SERIAL PRIMARY KEY,
                image BYTEA NOT NULL,
                label TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))
        conn.commit()
        logging.info(f"[DB] Table '{table_name}' created or already exists.")
        cur.close()
        conn.close()
    except Exception as e:
        logging.error(f"[DB ERROR] Table '{table_name}' creation failed: {e}")
        raise e


def insert_image_record(db_name, table_name, image_path, label):
    """Inserts image bytes and label into the specified table."""
    try:
        with open(image_path, 'rb') as f:
            binary_data = f.read()

        conn = psycopg2.connect(
            database=db_name,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cur = conn.cursor()
        cur.execute(
            sql.SQL("INSERT INTO {} (image, label) VALUES (%s, %s)").format(sql.Identifier(table_name)),
            (binary_data, label)
        )
        conn.commit()
        logging.info(f"[DB] Image record inserted into '{table_name}'.")
        cur.close()
        conn.close()
    except Exception as e:
        logging.error(f"[DB ERROR] Failed to insert image into '{table_name}': {e}")
        raise e


def fetch_last_image_record(db_name, table_name):
    """Fetches the last inserted image record from the specified table."""
    try:
        conn = psycopg2.connect(
            database=db_name,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cur = conn.cursor()
        cur.execute(sql.SQL("SELECT * FROM {} ORDER BY id DESC LIMIT 1;").format(sql.Identifier(table_name)))
        record = cur.fetchone()
        cur.close()
        conn.close()
        return record
    except Exception as e:
        logging.error(f"[DB ERROR] Fetching last record from '{table_name}' failed: {e}")
        return None


def clear_temp_table(db_name, temp_table="temp_image_data"):
    """Truncates the temporary table after processing."""
    try:
        conn = psycopg2.connect(
            database=db_name,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cur = conn.cursor()
        cur.execute(sql.SQL("TRUNCATE TABLE {};").format(sql.Identifier(temp_table)))
        conn.commit()
        logging.info(f"[DB] Temporary table '{temp_table}' cleared.")
        cur.close()
        conn.close()
    except Exception as e:
        logging.error(f"[DB ERROR] Failed to clear table '{temp_table}': {e}")
        raise e



