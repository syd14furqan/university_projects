import streamlit as st
import requests

st.set_page_config(page_title="Sentiment Analysis", page_icon="😊", layout="centered")

st.title("📊 Sentiment Analysis App")
st.write("Type some text below and see if it's Positive, Negative, or Neutral.")

# Input box
user_input = st.text_area("Enter your text:")

# Submit button
if st.button("Analyze Sentiment"):
    if user_input.strip() != "":
        try:
            response = requests.post(
                "http://127.0.0.1:8000/predict",
                json={"text": user_input}
            )
            if response.status_code == 200:
                result = response.json()
                label = result.get("label", "Unknown")
                score = result.get("score", 0)

                if label.lower() == "positive":
                    st.success(f"Positive 😀 (Score: {score:.4f})")
                elif label.lower() == "negative":
                    st.error(f"Negative 😡 (Score: {score:.4f})")
                else:
                    st.warning(f"Neutral 😐 (Score: {score:.4f})")
            else:
                st.error("⚠️ API returned an error.")
        except requests.exceptions.RequestException:
            st.error("❌ Could not connect to backend API.")
    else:
        st.warning("Please enter some text first.")
