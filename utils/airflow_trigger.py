import requests
import datetime
import base64

def trigger_airflow_dag():
    url = "http://airflow:8080/api/v1/dags/rock_paper_scissors_retrain_pipeline/dagRuns"

    user_pass = "admin:admin"
    b64_encoded = base64.b64encode(user_pass.encode("utf-8")).decode("utf-8")

    headers = {
        "Authorization": f"Basic {b64_encoded}",
        "Content-Type": "application/json"
    }

    payload = {
        "dag_run_id": f"run_{datetime.datetime.utcnow().isoformat()}",
        "conf": {}
    }

    res = requests.post(url, headers=headers, json=payload)

    if res.status_code != 200:
        raise Exception(f"Airflow DAG trigger failed: {res.text}")
