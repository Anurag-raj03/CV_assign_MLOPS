import requests
import datetime
import base64

def trigger_airflow_dag():
    url = "http://airflow:8080/api/v1/dags/rock_paper_scissors_retrain_pipeline/dagRuns"
    headers = {
        "Authorization": "Basic " + base64.b64encode(b"airflow:airflow").decode("utf-8"),
        "Content-Type": "application/json"
    }
    payload = {
        "dag_run_id": f"run_{datetime.datetime.utcnow().isoformat()}",
        "conf": {}
    }
    print("[Airflow Trigger] Sending DAG run request:", payload)
    res = requests.post(url, headers=headers, json=payload)
    print("[Airflow Response]", res.status_code, res.text)

    if res.status_code != 200:
        raise Exception(f"Airflow DAG trigger failed: {res.text}")
