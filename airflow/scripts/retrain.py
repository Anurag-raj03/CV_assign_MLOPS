from airflow.decorators import task

@task
def train_and_log_task(preprocessed_path: str):
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

    from src.model_making.model_resiter import register_model

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    try:
        logging.info(f"Using preprocessed data path: {preprocessed_path}")
        if not os.path.exists(preprocessed_path):
            raise FileNotFoundError(f"Preprocessed path does not exist: {preprocessed_path}")

        class_folders = os.listdir(preprocessed_path)
        total_images = sum([len(files) for r, d, files in os.walk(preprocessed_path)])
        if total_images == 0:
            raise ValueError(f"No images found in preprocessed path: {preprocessed_path}")

        logging.info("Setting up MLflow...")
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

        logging.info("Starting training...")
        with mlflow.start_run():
            history = model.fit(train_generator, epochs=5, validation_data=val_generator)

            final_train_acc = history.history["accuracy"][-1]
            final_val_acc = history.history["val_accuracy"][-1]

            mlflow.log_param("base_model", "MobileNetV2")
            mlflow.log_param("epochs", 5)
            mlflow.log_param("image_size", "224x224")
            mlflow.log_metric("train_accuracy", final_train_acc)
            mlflow.log_metric("val_accuracy", final_val_acc)

            logging.info("Predicting on sample from preprocessed input...")
            sample_images = []
            for label in os.listdir(preprocessed_path):
                label_path = os.path.join(preprocessed_path, label)
                for file in os.listdir(label_path):
                    if file.endswith(('.jpg', '.jpeg', '.png')):
                        img_path = os.path.join(label_path, file)
                        img = Image.open(img_path).resize((224, 224))
                        sample_images.append(np.array(img) / 255.0)
                        if len(sample_images) == 5:
                            break
                if len(sample_images) == 5:
                    break

            x_sample = np.array(sample_images)
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
            logging.info("Model saved to 'artifacts/rps_model_mobilenet.h5'")

        logging.info("Registering model with MLflow...")
        register_model()

    except Exception as e:
        logging.error(f"Training or logging failed: {str(e)}")
