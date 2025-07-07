import streamlit as st
import requests

st.set_page_config(page_title="✊ RPS Predictor", layout="centered")
st.title("🖼️ Rock Paper Scissors Predictor (Upload Only)")

FRAME_CAPTURE_URL = "http://backend:8000/predict/"
FINISH_URL = "http://backend:8000/finish/"

# Session state
if 'prediction_count' not in st.session_state:
    st.session_state.prediction_count = 0
if 'dag_triggered' not in st.session_state:
    st.session_state.dag_triggered = False

# Upload section
uploaded_file = st.file_uploader("📤 Upload an image (jpg, jpeg, png)", type=["jpg", "jpeg", "png"])
predict_btn = st.button("🔍 Predict")

if uploaded_file and predict_btn:
    files = {'image': (uploaded_file.name, uploaded_file.read(), 'image/jpeg')}
    try:
        res = requests.post(FRAME_CAPTURE_URL, files=files)
        if res.status_code == 200:
            prediction = res.json().get("prediction", "Unknown")
            st.success(f"🎯 Prediction: **{prediction}**")
            st.session_state.prediction_count += 1
        else:
            st.error("⚠️ Backend returned an error.")
    except Exception as e:
        st.error(f"❌ API Error: `{e}`")

# Auto-trigger DAG after 50 predictions
if st.session_state.prediction_count >= 50 and not st.session_state.dag_triggered:
    try:
        res = requests.post(FINISH_URL)
        if res.status_code == 200:
            st.success("🚀 DAG triggered automatically after 50 predictions!")
            st.session_state.dag_triggered = True
        else:
            st.warning("⚠️ Automatic DAG trigger failed.")
    except Exception as e:
        st.warning(f"❌ Error contacting backend: `{e}`")
