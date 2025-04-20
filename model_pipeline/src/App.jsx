import React, { useEffect, useState, useRef } from 'react';
import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';

const App = () => {
  const [isBotActive, setIsBotActive] = useState(false);
  const [conversationLog, setConversationLog] = useState([]);
  const [awaitingInput, setAwaitingInput] = useState(false);
  const [productContext, setProductContext] = useState("");

  const {
    transcript,
    listening,
    resetTranscript,
    browserSupportsSpeechRecognition,
  } = useSpeechRecognition();

  const debounceTimeout = useRef(null);

  useEffect(() => {
    if (browserSupportsSpeechRecognition) {
      SpeechRecognition.startListening({ continuous: true });
    }
  }, []);

  useEffect(() => {
    if (transcript.trim()) {
      console.log("Live transcript:", transcript);
    }
  }, [transcript]);

  useEffect(() => {
    const cleanedTranscript = transcript.toLowerCase().trim();
    if (!isBotActive && cleanedTranscript.includes('coffee')) {
      setIsBotActive(true);
      SpeechRecognition.stopListening();
      resetTranscript();

      speak('Hello! How can I help you today?', () => {
        resetTranscript();
        setAwaitingInput(true);
        SpeechRecognition.startListening({ continuous: true });
      });
    }
  }, [transcript]);

  useEffect(() => {
    if (isBotActive && awaitingInput && transcript.trim()) {
      const cleaned = transcript.trim().toLowerCase();
      if (cleaned === "coffee") return;

      if (debounceTimeout.current) {
        clearTimeout(debounceTimeout.current);
      }

      debounceTimeout.current = setTimeout(() => {
        const userMessage = transcript.trim();
        if (userMessage) {
          console.log('Final user input:', userMessage);
          setConversationLog((prev) => [...prev, { role: 'user', text: userMessage }]);
          resetTranscript();
          setAwaitingInput(false);
          fetchResponse(userMessage);
        }
      }, 1500);
    }
  }, [transcript]);

  const fetchResponse = async (message) => {
    try {
      const recentMemory = getMemory();

      const res = await fetch("http://localhost:5000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message,
          memory: recentMemory,
          context_memory: productContext,
        }),
      });

      const data = await res.json();
      const botReply = data.response;

      setProductContext(data.product_context || "");
      setConversationLog((prev) => [...prev, { role: 'bot', text: botReply }]);

      speak(botReply, () => {
        resetTranscript();
        setAwaitingInput(true);
        SpeechRecognition.startListening({ continuous: true });
      });
    } catch (error) {
      console.error("Error contacting backend:", error);
    }
  };

  const getMemory = () => {
    const exchanges = [];
    for (let i = conversationLog.length - 1; i >= 0; i--) {
      if (conversationLog[i].role === 'bot' || conversationLog[i].role === 'user') {
        exchanges.unshift(conversationLog[i]);
        if (exchanges.length >= 6) break;
      }
    }
    return exchanges;
  };

  const speak = (text, onEndCallback = () => {}) => {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1;
    utterance.pitch = 1;
    utterance.onend = () => {
      console.log('Speech finished. Restarting listener...');
      onEndCallback();
    };
    SpeechRecognition.stopListening();
    speechSynthesis.speak(utterance);
  };

  return (
    <main style={styles.container}>
      <h1 style={styles.header}>Blind-Assist Voice Chatbot</h1>
      <div role="log" aria-live="polite" style={styles.chatBox}>
        {conversationLog.map((entry, index) => (
          <p key={index} style={entry.role === 'user' ? styles.userText : styles.botText}>
            <strong>{entry.role === 'user' ? 'You: ' : 'Bot: '}</strong>{entry.text}
          </p>
        ))}
        {!isBotActive && (
          <p style={{ color: '#666', fontStyle: 'italic' }}>
            Say <strong>"coffee"</strong> to activate the bot...
          </p>
        )}
      </div>
      {isBotActive && (
        <p style={styles.status}>
          {listening ? '🎙️ Listening...' : '🛑 Not listening'}
        </p>
      )}
    </main>
  );
};

const styles = {
  container: {
    padding: '2rem',
    fontFamily: 'Arial, sans-serif',
    backgroundColor: '#f5f5f5',
    minHeight: '100vh',
  },
  header: {
    fontSize: '1.8rem',
    marginBottom: '1rem',
  },
  chatBox: {
    background: '#fff',
    padding: '1rem',
    borderRadius: '8px',
    maxHeight: '400px',
    overflowY: 'auto',
    marginBottom: '1rem',
  },
  userText: {
    textAlign: 'right',
    color: '#333',
  },
  botText: {
    textAlign: 'left',
    color: '#007BFF',
  },
  status: {
    fontSize: '1rem',
    color: '#333',
  },
};

export default App;
