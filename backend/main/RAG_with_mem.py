from fastapi import FastAPI
from pydantic import BaseModel
from langchain_ollama import ChatOllama
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from langchain_core.messages import HumanMessage, SystemMessage
from fastapi.middleware.cors import CORSMiddleware
import os
from langchain_ollama import OllamaEmbeddings

# Setup
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Set to ["http://localhost:3000"] in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# LLM and embeddings
llm = ChatOllama(model="gemma3:1b")
embedding = OllamaEmbeddings(model="nomic-embed-text:latest")  # You must have this embedding model pulled

# Path to FAISS index
faiss_path = "chat_memory_faiss"

# Load or create FAISS index
if os.path.exists(os.path.join(faiss_path, "index.faiss")):
    print("Loading existing FAISS index...")
    vectorstore = FAISS.load_local(faiss_path, embeddings=embedding, allow_dangerous_deserialization=True)
else:
    print("Creating new FAISS index...")
    dummy_doc = [Document(page_content="init", metadata={})]
    vectorstore = FAISS.from_documents(dummy_doc, embedding)
    
    # 🧠 Grab the ID of the inserted doc to delete it
    dummy_id = list(vectorstore.index_to_docstore_id.values())[0]
    vectorstore.delete([dummy_id])
    
    vectorstore.save_local(faiss_path)

# System prompt (not stored in vector DB)
system_prompt = SystemMessage(content="You are a helpful AI Assistant. Answer the User's queries succinctly in one sentence.")

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    # Save user's question to FAISS
    user_doc = Document(page_content=req.message, metadata={"role": "user"})
    vectorstore.add_documents([user_doc])

    # Retrieve context from FAISS
    similar_docs = vectorstore.similarity_search(req.message, k=3)
    context = "\n".join(doc.page_content for doc in similar_docs)

    # Build message history (system prompt + retrieved context + user input)
    messages = [
        system_prompt,
        HumanMessage(content=f"Context: {context}\nUser: {req.message}")
    ]

    # Generate response from LLM
    response = llm.invoke(messages)

    # Save AI's reply
    ai_doc = Document(page_content=response.content, metadata={"role": "ai"})
    vectorstore.add_documents([ai_doc])

    # Save updated index
    vectorstore.save_local(faiss_path)

    return ChatResponse(response=response.content)

@app.get("/history")
async def get_history():
    # Retrieve the stored messages in history (only recent context)
    docs = vectorstore.similarity_search("", k=100)
    return [
        {"role": doc.metadata.get("role", "unknown"), "content": doc.page_content}
        for doc in docs
    ]

@app.post("/reset")
async def reset_chat():
    try:
        # Check if the FAISS index directory exists and remove files
        if os.path.exists(faiss_path):
            print(f"Found FAISS directory, attempting to delete files in {faiss_path}")
            
            # Ensure the directory isn't empty before removing
            files_in_directory = os.listdir(faiss_path)
            if files_in_directory:
                for file in files_in_directory:
                    file_path = os.path.join(faiss_path, file)
                    os.remove(file_path)
                    print(f"Removed file: {file_path}")
                os.rmdir(faiss_path)
                print(f"FAISS directory deleted: {faiss_path}")
            else:
                print(f"FAISS directory is already empty.")
        else:
            print(f"No FAISS directory found at {faiss_path}. Skipping deletion.")

        # Reinitialize empty vectorstore
        print("Reinitializing vectorstore...")
        global vectorstore
        vectorstore = FAISS.from_documents([], embedding)
        print("Vectorstore reinitialized.")

        return {"message": "Chat memory has been reset."}
    
    except Exception as e:
        print(f"Error during reset: {e}")
        return {"message": f"Error resetting chat memory: {e}"}, 500



