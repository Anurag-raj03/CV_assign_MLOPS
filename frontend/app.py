# File: frontend/app.py
import streamlit as st
import requests
import time
import cv2
import os
import tempfile

st.set_page_config(page_title="RPS Predictor", layout="centered")
st.title("📸 Rock Paper Scissors - Predict via Upload or Camera")

FRAME_CAPTURE_URL = "http://backend:8000/predict/"
FINISH_URL = "http://backend:8000/finish/"

if 'prediction_count' not in st.session_state:
    st.session_state.prediction_count = 0
if 'dag_triggered' not in st.session_state:
    st.session_state.dag_triggered = False
if 'camera_active' not in st.session_state:
    st.session_state.camera_active = False
if 'camera_images' not in st.session_state:
    st.session_state.camera_images = []

uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
predict_btn = st.button("Predict")
reset_btn = st.button("Reset Session")
camera_btn = st.button("Start Camera")
stop_camera_btn = st.button("Stop Camera")

# Predict via upload
if uploaded_file and predict_btn:
    files = {'image': (uploaded_file.name, uploaded_file.read(), 'image/jpeg')}
    try:
        res = requests.post(FRAME_CAPTURE_URL, files=files)
        if res.status_code == 200:
            prediction = res.json().get("prediction", "Unknown")
            st.success(f"Prediction: {prediction}")
            st.session_state.prediction_count += 1
        else:
            st.error("Backend error.")
    except Exception as e:
        st.error(f"API error: {e}")

# Realtime Camera Prediction
if camera_btn:
    st.session_state.camera_active = True
    st.session_state.camera_images = []

if stop_camera_btn:
    st.session_state.camera_active = False

if st.session_state.camera_active:
    st.warning("📷 Camera running... Capturing frames")
    cap = cv2.VideoCapture(0)
    img_count = 0
    placeholder = st.empty()

    while cap.isOpened() and img_count < 50 and st.session_state.camera_active:
        ret, frame = cap.read()
        if not ret:
            st.error("Camera failure.")
            break

        img_path = os.path.join(tempfile.gettempdir(), f"frame_{img_count}.jpg")
        cv2.imwrite(img_path, frame)
        with open(img_path, "rb") as img_file:
            files = {'image': (f"frame_{img_count}.jpg", img_file, 'image/jpeg')}
            try:
                res = requests.post(FRAME_CAPTURE_URL, files=files)
                if res.status_code == 200:
                    pred = res.json().get("prediction", "Unknown")
                    st.session_state.prediction_count += 1
                else:
                    st.warning("Frame prediction failed.")
            except Exception as e:
                st.warning(f"Prediction error: {e}")

        st.session_state.camera_images.append(img_path)

        img_count += 1
        placeholder.image(frame, caption=f"Frame {img_count}", channels="BGR")
        st.info(f"⏱️ Next capture in 3...2...1...")
        time.sleep(1)

    cap.release()
    st.session_state.camera_active = False
    st.success("✅ 50 images captured and predictions done!")

if st.session_state.prediction_count > 0 and not st.session_state.dag_triggered:
    if st.button("Finish and Trigger DAG"):
        try:
            res = requests.post(FINISH_URL)
            if res.status_code == 200:
                st.success("🎯 DAG triggered successfully")
                st.session_state.dag_triggered = True
            else:
                st.warning("DAG trigger failed.")
        except Exception as e:
            st.warning(f"Error contacting backend: {e}")

if reset_btn:
    st.session_state.prediction_count = 0
    st.session_state.dag_triggered = False
    st.session_state.camera_images = []
    st.experimental_rerun()
