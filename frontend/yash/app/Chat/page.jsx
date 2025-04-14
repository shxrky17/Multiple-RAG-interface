"use client";

import { useState } from "react";

export default function ChatInterface() {
  const [messages, setMessages] = useState([
    { role: "assistant", content: "Hi! How can I help you today?" },
  ]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;
  
    const newMessage = { role: "user", content: input.trim() };
    setMessages((prev) => [...prev, newMessage]);
    setInput("");
    setIsTyping(true);
  
    try {
      const res = await fetch("http://localhost:8001/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content: newMessage.content }),
      });
  
      const data = await res.json();
      const botResponse = data?.content || "Sorry, I couldn't process that.";
  
      // Add an empty assistant message first
      setMessages((prev) => [...prev, { role: "assistant", content: "" }]);
  
      let index = 0;
      const typingInterval = setInterval(() => {
        setMessages((prev) => {
          return prev.map((msg, idx) => {
            if (idx === prev.length - 1) {
              // Append only one new character at a time
              return { ...msg, content: msg.content + botResponse[index] };
            }
            return msg;
          });
        });
  
        index++;
  
        if (index === botResponse.length) {
          clearInterval(typingInterval);
          setIsTyping(false);
        }
      }, 50); // Adjust speed if needed
  
    } catch (error) {
      console.error("Error fetching response:", error);
      setMessages((prev) => [...prev, { role: "assistant", content: "Error fetching response." }]);
      setIsTyping(false);
    }
  };
  
  
  

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-100">
      <div className="flex-1 p-4 overflow-y-auto space-y-4">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`max-w-[75%] px-4 py-2 rounded-lg ${
              msg.role === "user"
                ? "bg-blue-500 text-white self-end ml-auto"
                : "bg-white text-gray-800 self-start mr-auto"
            }`}
          >
            {msg.content}
          </div>
        ))}
        {isTyping && (
          <div className="bg-white text-gray-500 self-start mr-auto px-4 py-2 rounded-lg">
            Typing...
          </div>
        )}
      </div>
      <div className="p-4 border-t bg-white flex gap-2">
        <textarea
          rows={1}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type your message..."
          className="flex-1 p-2 border rounded resize-none"
        />
        <button
          onClick={sendMessage}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Send
        </button>
      </div>
    </div>
  );
}
