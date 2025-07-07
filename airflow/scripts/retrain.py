# from airflow.decorators import task
# @task
def train_and_log_task(preprocessed_path: str):
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

    w.filterwarnings('ignore')
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from src.model_making.model_resiter import register_model

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    try:
        if not os.path.exists(preprocessed_path):
            raise FileNotFoundError(f"Path not found: {preprocessed_path}")

        total_images = sum([len(files) for _, _, files in os.walk(preprocessed_path)])
        if total_images == 0:
            raise ValueError("No images found in the given directory.")

        mlflow.set_tracking_uri("http://mlflow:5000")
        mlflow.set_experiment("play-rock-paper-scissors-exp")

        datagen = ImageDataGenerator(validation_split=0.2, rescale=1. / 255)

        train_generator = datagen.flow_from_directory(
            preprocessed_path,
            target_size=(224, 224),
            batch_size=16,
            subset="training",
            class_mode="categorical"
        )

        val_generator = datagen.flow_from_directory(
            preprocessed_path,
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
            artifact_dir = os.path.join(os.getcwd(), "artifacts")
            os.makedirs(artifact_dir, exist_ok=True)
            model_path = os.path.join(artifact_dir, "rps_model_mobilenet.h5")
            model.save(model_path)
            logging.info(f"Model saved at: {model_path}")
            sample_images = []
            for label in os.listdir(preprocessed_path):
                label_path = os.path.join(preprocessed_path, label)
                if not os.path.isdir(label_path):
                    continue
                for file in os.listdir(label_path):
                    if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                        try:
                            img_path = os.path.join(label_path, file)
                            img = Image.open(img_path).convert("RGB").resize((224, 224))
                            sample_images.append(np.array(img) / 255.0)
                            if len(sample_images) == 5:
                                break
                        except Exception as img_err:
                            logging.warning(f"Skipping image due to error: {img_err}")
                if len(sample_images) == 5:
                    break

            if len(sample_images) == 0:
                raise ValueError("No valid sample images found.")

            x_sample = np.array(sample_images)
            if x_sample.ndim == 3:
                x_sample = np.expand_dims(x_sample, axis=0)

            
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

            logging.info("Model logged to MLflow successfully.")

        register_model()
        logging.info("Model registration completed.")

    except Exception as e:
        logging.error(f"Training or logging failed: {str(e)}", exc_info=True)
