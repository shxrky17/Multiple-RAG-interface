import uvicorn
import httpx
import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv
load_dotenv()
# Set up Groq API key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")  # Set this in your .env file
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (for testing)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model
class ChatRequest(BaseModel):
    content: str  # Expects JSON: { "content": "message" }

# Response model
class ChatMessage(BaseModel):
    role: str
    content: str

# In-memory chat history
chat_history = []

# ✅ POST: Send user message to Groq API
@app.post("/chat", response_model=ChatMessage)
async def chat_with_groq(request: ChatRequest):
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "gemma2-9b-it",  # ✅ Change to a supported model
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},  
                {"role": "user", "content": request.content}
            ]
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(GROQ_API_URL, json=payload, headers=headers)

        if response.status_code == 200:
            data = response.json()
            ai_response = data["choices"][0]["message"]["content"]

            # Save to chat history
            chat_history.append({"role": "user", "content": request.content})
            chat_history.append({"role": "assistant", "content": ai_response})

            return ChatMessage(role="assistant", content=ai_response)

        else:
            print(f"Error: {response.text}")  # Debugging
            raise HTTPException(status_code=response.status_code, detail=response.text)

    except Exception as e:
        print(f"Exception: {e}")  # Debugging
        raise HTTPException(status_code=500, detail=str(e))

# ✅ GET: Fetch chat history
@app.get("/chats", response_model=List[ChatMessage])
async def get_chat_history():
    return chat_history

# ✅ Run server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
