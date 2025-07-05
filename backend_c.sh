set -e
set -o pipefail

echo "[DVC] Setting up DVC..."

if [ ! -d ".dvc" ]; then
    echo "Initializing DVC without SCM..."
    dvc init --no-scm
fi

if [ ! -f "Data.dvc" ]; then
    echo " Adding Data_kind_stack to DVC..."
    dvc add Data
    dvc commit -m "Added Data"
else
    echo "Data already tracked by DVC"
fi

echo "Initializing Database & Tables..."
python Database_connection/db_tb.py

echo "Inserting Dummy Data..."
python Database_connection/testing_record_airflow.py

echo "Launching the app..."
uvicorn main:app --host 0.0.0.0 --port 8000
