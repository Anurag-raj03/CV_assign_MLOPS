import os
import sys
import mlflow
import mlflow.keras
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
import tensorflow as tf

w.filterwarnings('ignore')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from data_ingestion.ingestion import validate_and_ingest_image
from preprocessing.preprocess_image import preprocess_images

def train_and_log_model():
    validate_and_ingest_image("src/main_dataset/main_raw_data", "Data/raw_data")
    preprocess_images("Data/raw_data", "Data/src_preprocessed_data")

    mlflow.set_tracking_uri("http://mlflow:5000")
    mlflow.set_experiment("play-rock-paper-scissors-exp")

    datagen = ImageDataGenerator(validation_split=0.2, rescale=1. / 255)

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

    base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(128, activation="relu")(x)
    predictions = Dense(3, activation="softmax")(x)
    model = Model(inputs=base_model.input, outputs=predictions)

    for layer in base_model.layers:
        layer.trainable = False

    model.compile(optimizer=Adam(), loss="categorical_crossentropy", metrics=["accuracy"])

    with mlflow.start_run():
        history = model.fit(train_generator, epochs=5, validation_data=val_generator)

        mlflow.log_param("base_model", "MobileNetV2")
        mlflow.log_param("epochs", 5)
        mlflow.log_param("image_size", "224x224")
        mlflow.log_metric("train_accuracy", history.history["accuracy"][-1])
        mlflow.log_metric("val_accuracy", history.history["val_accuracy"][-1])

        artifact_dir = os.path.abspath("artifacts")
        os.makedirs(artifact_dir, exist_ok=True)
        model_path = os.path.join(artifact_dir, "rps_model_mobilenet.h5")
        model.save(model_path)
        logging.info(f"Model saved to: {model_path}")

        sample_path = "src/main_dataset/sample_example_input"
        x_sample = []

        for subdir, _, files in os.walk(sample_path):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    try:
                        img_path = os.path.join(subdir, file)
                        img = Image.open(img_path).convert("RGB").resize((224, 224))
                        x_sample.append(np.array(img) / 255.0)
                        if len(x_sample) == 5:
                            break
                    except Exception as e:
                        logging.warning(f"Skipping image due to error: {file} -> {e}")
            if len(x_sample) == 5:
                break

        if len(x_sample) == 0:
            raise ValueError("No valid sample images found in sample_example_input.")

        x_sample = np.array(x_sample)
        if x_sample.ndim == 3:
            x_sample = np.expand_dims(x_sample, axis=0)

        tf.config.run_functions_eagerly(True)
        preds_sample = model.predict(x_sample)
        signature = infer_signature(x_sample, preds_sample)

        mlflow.keras.log_model(
            model,
            artifact_path="rps_cnn_model",
            signature=signature,
            pip_requirements=[
                "tensorflow-cpu==2.13.0",
                "keras==2.13.1",
                "mlflow==2.4.1",
                "pandas",
                "pillow==10.0.0"
            ]
        )

        logging.info("Model successfully logged to MLflow.")

if __name__ == "__main__":
    train_and_log_model()
