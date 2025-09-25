from fastapi import FastAPI, Body
from src.nlp.tokenization import simple_whitespace_tokenize
from src.nlp.embeddings import dummy_embed
from src.nlp.pipelines.chat import echo_chat_pipeline

app = FastAPI(title="AI Portfolio API")

@app.get("/health")
def health():
    return {"status": "ok"}

# --- Day 5: NLP stub routes ---
@app.get("/nlp/health")
def nlp_health():
    return {"status": "ok", "module": "nlp"}

@app.post("/nlp/tokenize")
def nlp_tokenize(payload: dict = Body(...)):
    text = payload.get("text", "")
    return {"tokens": simple_whitespace_tokenize(text)}

@app.post("/nlp/embed")
def nlp_embed(payload: dict = Body(...)):
    texts = payload.get("texts", [])
    return {"embeddings": dummy_embed(texts)}

@app.post("/nlp/chat")
def nlp_chat(payload: dict = Body(...)):
    msg = payload.get("message", "")
    temperature = payload.get("temperature", 0.0)
    return echo_chat_pipeline(msg, temperature=temperature)
