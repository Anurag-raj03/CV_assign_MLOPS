import os
import sys
import mlflow
import mlflow.tensorflow
import numpy as np
import logging
import warnings as w
from PIL import Image

from keras.preprocessing.image import ImageDataGenerator
from keras.applications import MobileNetV2
from keras.models import Model
from keras.layers import Dense, GlobalAveragePooling2D
from keras.optimizers import Adam
from mlflow.models.signature import infer_signature

w.filterwarnings('ignore')
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from data_ingestion.ingestion import validate_and_ingest_image
from preprocessing.preprocess_image import preprocess_images

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def train_and_log_model():
    try:
        logging.info("Validating and ingesting raw images...")
        validate_and_ingest_image("src/main_dataset/main_raw_data", "Data/raw_data")

        logging.info("Preprocessing images...")
        preprocess_images("Data/raw_data", "Data/src_preprocessed_data")

        logging.info("Setting up MLflow tracking...")
        mlflow.set_tracking_uri("http://mlflow:5000")
        mlflow.set_experiment("play-rock-paper-scissors-exp")

        logging.info("Preparing data generators...")
        datagen = ImageDataGenerator(validation_split=0.2, rescale=1./255)

        train_generator = datagen.flow_from_directory(
            "Data/src_preprocessed_data",
            target_size=(224, 224),
            batch_size=16,
            subset="training",
            class_mode="categorical"
        )

        val_generator = datagen.flow_from_directory(
            "Data/src_preprocessed_data",
            target_size=(224, 224),
            batch_size=16,
            subset="validation",
            class_mode="categorical"
        )

        logging.info("Building MobileNetV2 model...")
        base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
        x = base_model.output
        x = GlobalAveragePooling2D()(x)
        x = Dense(128, activation="relu")(x)
        predictions = Dense(3, activation="softmax")(x)
        model = Model(inputs=base_model.input, outputs=predictions)

        for layer in base_model.layers:
            layer.trainable = False

        model.compile(optimizer=Adam(), loss="categorical_crossentropy", metrics=["accuracy"])

        logging.info("Training started...")
        with mlflow.start_run():
            history = model.fit(train_generator, epochs=5, validation_data=val_generator)

            final_train_acc = history.history["accuracy"][-1]
            final_val_acc = history.history["val_accuracy"][-1]

            mlflow.log_param("base_model", "MobileNetV2")
            mlflow.log_param("epochs", 5)
            mlflow.log_param("image_size", "224x224")
            mlflow.log_metric("train_accuracy", final_train_acc)
            mlflow.log_metric("val_accuracy", final_val_acc)

            logging.info("Performing prediction on sample inputs...")
            sample_path = r"src/main_dataset/sample_example_input"
            if not os.path.exists(sample_path):
                raise FileNotFoundError(f"Sample path not found: {sample_path}")

            x_sample = []
            for file in os.listdir(sample_path):
                if file.endswith(('.png', '.jpg', '.jpeg')):
                    img = Image.open(os.path.join(sample_path, file)).resize((224, 224))
                    img = np.array(img) / 255.0
                    x_sample.append(img)

            x_sample = np.array(x_sample)
            if x_sample.ndim == 3:
                x_sample = np.expand_dims(x_sample, axis=0)

            preds_sample = model.predict(x_sample)
            signature = infer_signature(x_sample, preds_sample)

            mlflow.tensorflow.log_model(
                model,
                artifact_path="rps_cnn_model",
                signature=signature
            )

            os.makedirs("artifacts", exist_ok=True)
            model.save("artifacts/rps_model_mobilenet.h5")
            logging.info("Model saved locally to 'artifacts/rps_model_mobilenet.h5'")

    except Exception as e:
        logging.error(f"Error occurred during training or logging: {str(e)}")


