import sys
import os
import logging
from train_model import train_and_log_model
from model_resiter import register_model
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    
    try:
        logging.info("Starting ML pipeline for COMPUTER VISION PROJECTS...")
        
        train_and_log_model()

        logging.info("Model training and MLflow logging completed successfully.")

        register_model()
        

        logging.info("Model registration completed.")

    except Exception as e:
        logging.error(f"Pipeline failed due to error: {e}")