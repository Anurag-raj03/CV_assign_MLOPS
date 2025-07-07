#!/bin/bash

set -e



echo "Configuring DVC remote..."
dvc remote modify --local myremote access_key_id $AWS_ACCESS_KEY_ID
dvc remote modify --local myremote secret_access_key $AWS_SECRET_ACCESS_KEY
dvc remote modify --local myremote region $AWS_DEFAULT_REGION

echo "Running DVC push..."
dvc push

echo "Initializing database..."
python Database_connection/db_tb.py

echo "Inserting dummy data..."
python Database_connection/testing_record_airflow.py

echo "Starting backend API..."
uvicorn main:app --host 0.0.0.0 --port 8000
