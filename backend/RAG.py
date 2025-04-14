from fastapi import FastAPI, Request
from pydantic import BaseModel
import ollama
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI app
app = FastAPI()

# Allow frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, use your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load dataset
with open('/home/yash/Desktop/Langchain/hi.txt', 'r') as file:
    dataset = [line.strip() for line in file if line.strip()]

EMBEDDING_MODEL = 'nomic-embed-text:latest'
LANGUAGE_MODEL = 'gemma3:1b'

VECTOR_DB = []

# Embed dataset once
for chunk in dataset:
    result = ollama.embed(model=EMBEDDING_MODEL, input=chunk)
    embedding = result.get('embedding') or result.get('embeddings', [None])[0]
    if embedding:
        VECTOR_DB.append((chunk, embedding))

# Cosine similarity
def cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x ** 2 for x in a) ** 0.5
    norm_b = sum(x ** 2 for x in b) ** 0.5
    return dot / (norm_a * norm_b)

# Retrieve similar chunks
def retrieve(query, top_n=3):
    result = ollama.embed(model=EMBEDDING_MODEL, input=query)
    query_embedding = result.get('embedding') or result.get('embeddings', [None])[0]
    scores = [(chunk, cosine_similarity(query_embedding, emb)) for chunk, emb in VECTOR_DB]
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores[:top_n]

# Input structure
class Query(BaseModel):
    question: str

# API endpoint
@app.post("/ask")
def ask_bot(query: Query):
    input_query = query.question
    retrieved = retrieve(input_query)
    context = "\n".join([f" - {chunk}" for chunk, _ in retrieved])

    instruction_prompt = f"""You are a helpful chatbot.
Use only the following pieces of context to answer the question. Don't make up any new information:

{context}
"""

    response = ""
    for chunk in ollama.chat(
        model=LANGUAGE_MODEL,
        messages=[
            {"role": "system", "content": instruction_prompt},
            {"role": "user", "content": input_query}
        ],
        stream=True,
    ):
        response += chunk['message']['content']

    return {"response": response}

