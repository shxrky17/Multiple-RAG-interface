import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from fastapi import FastAPI

app = FastAPI()

# Define Models
class Fruit(BaseModel):
    name: str

class Fruits(BaseModel):
    fruits: List[Fruit]

# CORS Middleware
origins = [
    "http://localhost:3000",  # Corrected URL format
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # This must be a list
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory database
memory_db = {"fruits": []}

# Get Fruits
@app.get("/fruits", response_model=Fruits)
def get_fruits():
    return Fruits(fruits=memory_db["fruits"])

# Add a Fruit
@app.post("/fruits", response_model=Fruit)
def add_fruit(fruit: Fruit):
    memory_db["fruits"].append(fruit)
    return fruit

# Run the app
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
