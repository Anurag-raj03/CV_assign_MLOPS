from fastapi import FastAPI, UploadFile, HTTPException, BackgroundTasks
from prometheus_fastapi_instrumentator import Instrumentator
import sys
import os
import tempfile
import shutil

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from inference.predictor import load_model, predict_label
from Database_connection.db_init import insert_image_record
from utils.airflow_trigger import trigger_airflow_dag
from utils.predict_counter import increment_and_check


app = FastAPI(title="Rock Paper Scissors FastAPI Service")
Instrumentator().instrument(app).expose(app)

MODEL_PATH = "artifacts/rps_model_mobilenet.h5"
DB_NAME = "mlops_image_db"
PERM_TABLE = "image_data"
TEMP_TABLE = "temp_image_data"
model = load_model(MODEL_PATH)

@app.post("/predict/")
async def capture_and_predict(image: UploadFile, background_tasks: BackgroundTasks):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            shutil.copyfileobj(image.file, tmp)
            img_path = tmp.name

        label = predict_label(img_path, model)

        insert_image_record(DB_NAME, PERM_TABLE, img_path, label)
        insert_image_record(DB_NAME, TEMP_TABLE, img_path, label)

        os.remove(img_path)
        if increment_and_check():
            background_tasks.add_task(trigger_airflow_dag)

        return {"prediction": label}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


