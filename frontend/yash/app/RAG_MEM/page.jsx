"use client"
import { useEffect, useState } from "react";

export default function Home() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  // Fetch chat history when page loads
  useEffect(() => {
    fetch("http://127.0.0.1:8000/history")
      .then((res) => res.json())
      .then((data) => setMessages(data));
  }, []);

  // Send user message to backend
  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = { type: "human", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");

    const res = await fetch("http://127.0.0.1:8000/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message: input }),
    });
    const data = await res.json();

    const aiMessage = { type: "ai", content: data.response };
    setMessages((prev) => [...prev, aiMessage]);
  };

  // Reset chat history
  const handleReset = async () => {
    await fetch("http://127.0.0.1:8000/reset", {
      method: "POST",
    });
    setMessages([]);
  };

  return (
    <div style={{ maxWidth: 800, margin: "auto", padding: 20 }}>
      <h1>🧠 LangChain Chatbot</h1>

      <div
        style={{
          border: "1px solid #ccc",
          borderRadius: 8,
          padding: 16,
          minHeight: 300,
          marginBottom: 16,
          background: "#f9f9f9",
        }}
      >
        {messages.map((msg, index) => (
          <div
            key={index}
            style={{
              marginBottom: 8,
              textAlign: msg.type === "human" ? "right" : "left",
            }}
          >
            <span
              style={{
                backgroundColor: msg.type === "human" ? "#DCF8C6" : "#E8E8E8",
                padding: "8px 12px",
                borderRadius: 16,
                display: "inline-block",
              }}
            >
              {msg.content}
            </span>
          </div>
        ))}
      </div>

      <div style={{ display: "flex", gap: 8 }}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder="Type your message..."
          style={{
            flex: 1,
            padding: 10,
            borderRadius: 8,
            border: "1px solid #ccc",
          }}
        />
        <button onClick={handleSend} style={{ padding: "10px 16px" }}>
          Send
        </button>
        <button
          onClick={handleReset}
          style={{
            padding: "10px 16px",
            backgroundColor: "#f44336",
            color: "#fff",
            border: "none",
            borderRadius: 8,
          }}
        >
          Reset
        </button>
      </div>
    </div>
  );
}
