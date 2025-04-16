from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama

# Initialize the Ollama Model (adjust 'model' name as per your local Ollama setup)
llm = ChatOllama(model="gemma3:1b")  # or any model you've pulled like "mistral", "llama2", etc.

# Define System Prompt
system_prompt = SystemMessage(content="You are a helpful AI Assistant. Answer the User's queries succinctly in one sentence.")

# Start Storage for Historical Message History
messages = [system_prompt]

while True:
    # Get User's Message
    user_input = input("\nUser: ")
    
    if user_input.lower() == "exit":
        break

    user_message = HumanMessage(content=user_input)

    # Extend Messages List With User Message
    messages.append(user_message)

    # Pass Entire Message Sequence to LLM to Generate Response
    response = llm.invoke(messages)
    
    print("\nAI Message:", response.content)

    # Add AI's Response to Message List
    messages.append(response)

# Print all messages stored in the message list
for i, message in enumerate(messages):
    print(f"\nMessage {i+1} - {message.type.upper()}: {message.content}")

