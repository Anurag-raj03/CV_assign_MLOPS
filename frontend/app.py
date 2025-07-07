import streamlit as st
import requests

st.set_page_config(page_title="RPS Predictor", layout="centered")
st.title("Upload Rock Paper Scissors Image for Prediction")

FRAME_CAPTURE_URL = "http://backend:8000/predict/"
FINISH_URL = "http://backend:8000/finish/"

if 'prediction_count' not in st.session_state:
    st.session_state.prediction_count = 0
if 'dag_triggered' not in st.session_state:
    st.session_state.dag_triggered = False

uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
predict_btn = st.button("Predict")
reset_btn = st.button("Reset Session")

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

if st.session_state.prediction_count > 0 and not st.session_state.dag_triggered:
    if st.button("Finish and Trigger DAG"):
        try:
            res = requests.post(FINISH_URL)
            if res.status_code == 200:
                st.success("DAG triggered successfully")
                st.session_state.dag_triggered = True
            else:
                st.warning("DAG trigger failed.")
        except Exception as e:
            st.warning(f"Error contacting backend: {e}")

if reset_btn:
    st.session_state.prediction_count = 0
    st.session_state.dag_triggered = False
    st.experimental_rerun()
