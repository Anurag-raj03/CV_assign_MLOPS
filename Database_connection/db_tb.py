import time
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Database_connection.db_init import create_database, create_table

DB_NAME = "mlops_image_db"
TABLE1 = "temp_image_data"
TABLE2 = "image_data"

MAX_RETRIES = 10
for attempt in range(MAX_RETRIES):
    try:
        print(f"[Try {attempt+1}] Attempting DB setup...")
        create_database(DB_NAME)
        create_table(DB_NAME, TABLE1)
        create_table(DB_NAME, TABLE2)
        print("Database and tables created successfully.")
        break
    except Exception as e:
        print(f"Error during DB setup: {e}")
        if attempt < MAX_RETRIES - 1:
            time.sleep(5)
        else:
            print("Exceeded max retries. Failing...")
