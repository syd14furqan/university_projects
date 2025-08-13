# backend/main.py
from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="BERT Sentiment API")

# Allow calls from Streamlit (or any origin) during dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the sentiment pipeline once at startup
sentiment_pipeline = pipeline("sentiment-analysis")  # downloads model first time

class TextInput(BaseModel):
    text: str

@app.get("/")
async def root():
    return {"status": "ok", "message": "Sentiment API is running"}

@app.post("/predict")
async def predict(input: TextInput):
    result = sentiment_pipeline(input.text)[0]
    # Ensure JSON-serializable and small precision
    return {"label": result["label"], "score": round(float(result["score"]), 4)}
