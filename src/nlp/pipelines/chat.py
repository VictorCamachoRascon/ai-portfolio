from typing import Dict

def echo_chat_pipeline(message: str, **kwargs) -> Dict:
    """
    Minimal chat stub. Replace with actual LLM calls (FastAPI route uses this).
    """
    return {"reply": f"Echo: {message}", "meta": {"model": "stub", "temperature": kwargs.get("temperature", 0.0)}}
