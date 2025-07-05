from airflow import DAG
from airflow.utils.dates import days_ago
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
        db_name="rock_paper_db",
        table_name="temp_predictions",
        folder_extracted="Data/raw_data"
    )
    preprocess = preprocess_and_save_images.override(task_id="preprocess_images")(
        input_dir="Data/raw_data",
        output_dir="Data/for_retraining_prep",
        target_size=(224, 224),
        blur_threshold=50.0
    )
    retrain = train_and_log_task.override(task_id="retrain_rps_model")(
        preprocessed_path="Data/src_preprocessed_data"
    )

    extract >> preprocess >> retrain
