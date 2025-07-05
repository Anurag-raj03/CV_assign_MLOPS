import streamlit as st
import requests
import cv2
import time

st.set_page_config(page_title="✊ RPS Predictor", layout="centered")
st.title("🎥 Real-Time Rock Paper Scissors Detector")

FRAME_CAPTURE_URL = "http://localhost:8000/predict/"
FINISH_URL = "http://localhost:8000/finish/"

run = st.checkbox("🎬 Start Camera")

frame_window = st.empty()
prediction_placeholder = st.empty()
countdown_placeholder = st.empty()

if run:
    camera = cv2.VideoCapture(0)
    while True:
        ret, frame = camera.read()
        if not ret:
            st.error("Failed to read from camera.")
            break

        frame_window.image(frame, channels="BGR")

        for i in range(3, 0, -1):
            countdown_placeholder.markdown(f"⏳ Capturing next frame in **{i}** second(s)...")
            time.sleep(1)

        countdown_placeholder.markdown("📸 Capturing now...")

        _, img_encoded = cv2.imencode('.jpg', frame)
        files = {'image': ('frame.jpg', img_encoded.tobytes(), 'image/jpeg')}

        try:
            res = requests.post(FRAME_CAPTURE_URL, files=files)
            if res.status_code == 200:
                prediction = res.json().get("prediction", "Unknown")
                prediction_placeholder.markdown(f"### 🤖 Prediction: **{prediction}**")
        except Exception as e:
            prediction_placeholder.markdown("⚠️ API error.")

    camera.release()

else:
    try:
        res = requests.post(FINISH_URL)
        if res.status_code == 200:
            st.success("✅ Camera stopped. Airflow DAG triggered.")
        else:
            st.warning("⚠️ DAG trigger failed.")
    except Exception as e:
        st.warning("⚠️ Error contacting backend.")
