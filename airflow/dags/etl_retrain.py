from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.python import PythonOperator

from datetime import timedelta
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scripts.extract_img import extraction_image
from scripts.preprocess_load import preprocess_and_save_images
from scripts.retrain import train_and_log_task 

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

with DAG(
    dag_id='rock_paper_scissors_retrain_pipeline',
    default_args=default_args,
    description="Retraining pipeline for RPS ML model (Extract, Preprocess, Retrain)",
    schedule_interval=None,
    catchup=False,
    tags=["rps", "ml", "retrain"]
) as dag:

    extract = extraction_image.override(task_id="extract_images_from_postgres")(
        db_name="mlops_image_db",
        table_name="temp_image_data",
        folder_extracted="Data/raw_data"
    )

    preprocess = preprocess_and_save_images.override(task_id="preprocess_images")(
        input_dir="Data/raw_data",
        output_dir="Data/for_retraining_prep",
        target_size=(224, 224),
        blur_threshold=50.0
    )

    retrain = PythonOperator(
        task_id="retrain_rps_model",
        python_callable=train_and_log_task,
        op_kwargs={"preprocessed_path": "Data/for_retraining_prep"},
        execution_timeout=timedelta(hours=2)
    )

    extract >> preprocess >> retrain

    
