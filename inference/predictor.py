from keras.models import load_model as keras_load
from keras.preprocessing import image
import numpy as np

CLASS_MAP = {
    0: "rock",
    1: "paper",
    2: "scissors"
}

def load_model(path: str):
    model = keras_load(path)
    print("[Model Loaded] Mobilenet RPS Model")
    return model

def predict_label(image_path: str, model):
    img = image.load_img(image_path, target_size=(224, 224))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x /= 255.0

    pred = model.predict(x)
    class_index = np.argmax(pred, axis=1)[0]
    return CLASS_MAP[class_index]
