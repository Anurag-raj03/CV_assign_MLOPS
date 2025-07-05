import mlflow
from mlflow.exceptions import MlflowException
from mlflow.tracking import MlflowClient
import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def register_model():
    mlflow.set_tracking_uri("http://mlflow:5000")

    experiment_name = "play-rock-paper-scissors-exp"
    model_dir_name = "rps_cnn_model"
    registered_model_name = "RockPaperScissorsModel"

    try:
        experiment = mlflow.get_experiment_by_name(experiment_name)
        if experiment is None:
            experiment_id = mlflow.create_experiment(experiment_name)
            logger.info(f"New experiment '{experiment_name}' created with ID: {experiment_id}")
        else:
            experiment_id = experiment.experiment_id
            logger.info(f"Existing experiment '{experiment_name}' found with ID: {experiment_id}")

        client = MlflowClient()
        runs = client.search_runs(
            experiment_ids=[experiment_id],
            order_by=["start_time DESC"],
            max_results=1
        )

        if not runs:
            logger.warning("No recent runs found in the experiment.")
            return

        latest_run = runs[0]
        run_id = latest_run.info.run_id
        logger.info(f"Latest run ID: {run_id}")

        artifacts = client.list_artifacts(run_id)
        artifact_paths = [artifact.path for artifact in artifacts]

        if model_dir_name not in artifact_paths:
            logger.error(f"No model directory named '{model_dir_name}' found in run artifacts.")
            return

        logger.info(f"Model directory '{model_dir_name}' found. Proceeding to register...")

        model_uri = f"runs:/{run_id}/{model_dir_name}"

        result = mlflow.register_model(model_uri=model_uri, name=registered_model_name)
        logger.info(f"Model registered as '{registered_model_name}' (version: {result.version})")

    except MlflowException as e:
        logger.error(f"MLflow exception occurred during model registration: {e}")
    except Exception as e:
        logger.exception("Unexpected error during model registration")

if __name__ == "__main__":
    register_model()
