from fastapi import FastAPI, Depends, HTTPException, Header
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import ollama

load_dotenv()

API_KEY_CREDITS = {os.getenv("API_KEY"): 2}

app = FastAPI()

class PromptRequest(BaseModel):
    prompt: str

def verify_api_key(x_api_key: str = Header(None)) -> str:
    credits = API_KEY_CREDITS.get(x_api_key, 0)
    if credits <= 0:
        raise HTTPException(status_code=401, detail="Invalid or expired API key")
    return x_api_key

@app.post("/generate")
def generate(request: PromptRequest, x_api_key: str = Depends(verify_api_key)):
    API_KEY_CREDITS[x_api_key] -= 1
    try:
        response = ollama.chat(
            model="gemma3:1b",
            messages=[{"role": "user", "content": request.prompt}]
        )
        return {
            "response": response["message"]["content"],
            "remaining_credits": API_KEY_CREDITS[x_api_key]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
