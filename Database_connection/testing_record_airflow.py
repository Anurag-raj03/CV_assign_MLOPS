import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Database_connection.db_init import insert_image_record

DB_NAME = "mlops_image_db"
TABLE_NAME = "temp_image_data"

try:
    insert_image_record(DB_NAME, TABLE_NAME, "Data/raw_data/paper/0eqArS2GgsBeqgSn.png", "paper")
    print("Dummy image record inserted")
except Exception as e:
    print(f"Failed to insert image record: {e}")
