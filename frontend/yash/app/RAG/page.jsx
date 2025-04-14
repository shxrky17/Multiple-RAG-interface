"use client";

import { useState } from 'react';

export default function ChatPage() {
  const [question, setQuestion] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);

  const askBot = async () => {
    if (!question.trim()) return;

    setLoading(true);
    setResponse('');

    try {
      const res = await fetch('http://localhost:8000/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question }),
      });

      const data = await res.json();
      setResponse(data.response);
    } catch (err) {
      setResponse('Error talking to the chatbot.');
      console.error(err);
    }

    setLoading(false);
  };

  return (
    <div style={{ padding: '2rem', fontFamily: 'sans-serif' }}>
      <h1>Langchain Chatbot</h1>
      <textarea
        rows={4}
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="Ask a question..."
        style={{ width: '100%', marginBottom: '1rem', padding: '0.5rem' }}
      />
      <button onClick={askBot} disabled={loading}>
        {loading ? 'Thinking...' : 'Ask'}
      </button>

      <h3>Response:</h3>
      <pre style={{ background: '#f0f0f0', padding: '1rem' }}>{response}</pre>
    </div>
  );
}

