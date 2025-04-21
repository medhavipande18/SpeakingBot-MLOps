// App.jsx with speaking/listening indicators
import React, { useEffect, useState, useRef } from 'react';
import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';
import './App.css';

const App = () => {
  const [isBotActive, setIsBotActive] = useState(false);
  const [conversationLog, setConversationLog] = useState([]);
  const [awaitingInput, setAwaitingInput] = useState(false);
  const [productContext, setProductContext] = useState("");
  const [currentBotResponse, setCurrentBotResponse] = useState("");
  const [muted, setMuted] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);

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
      
      setCurrentBotResponse('Hello! How can I help you today?');
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

      const res = await fetch("/chat", {
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
      setCurrentBotResponse(botReply);

      if (!muted) {
        speak(botReply, () => {
          resetTranscript();
          setAwaitingInput(true);
          SpeechRecognition.startListening({ continuous: true });
        });
      } else {
        resetTranscript();
        setAwaitingInput(true);
        SpeechRecognition.startListening({ continuous: true });
      }
    } catch (error) {
      console.error("Error contacting backend:", error);
      
      // Fallback in case the backend is not responding
      const fallbackResponse = "I'm sorry, I couldn't connect to the server. Please try again later.";
      setCurrentBotResponse(fallbackResponse);
      
      if (!muted) {
        speak(fallbackResponse, () => {
          resetTranscript();
          setAwaitingInput(true);
          SpeechRecognition.startListening({ continuous: true });
        });
      } else {
        resetTranscript();
        setAwaitingInput(true);
        SpeechRecognition.startListening({ continuous: true });
      }
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
    if (muted) {
      onEndCallback();
      return;
    }
    
    setIsSpeaking(true);
    
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1;
    utterance.pitch = 1;
    utterance.onend = () => {
      console.log('Speech finished. Restarting listener...');
      setIsSpeaking(false);
      onEndCallback();
    };
    
    SpeechRecognition.stopListening();
    speechSynthesis.speak(utterance);
  };

  const toggleMute = () => {
    setMuted(!muted);
    if (speechSynthesis.speaking) {
      speechSynthesis.cancel();
      setIsSpeaking(false);
    }
  };

  return (
    <>
      <div className="navbar">
        <div className="nav-left">
          <div className="nav-link">Login</div>
          <div className="nav-link">Sign Up</div>
          <div className="cart-button">Cart</div>
        </div>
        <div className="nav-center">
          <div className="brand">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M18 6V4H6V6H4V8H20V6H18Z" stroke="#D4B483" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M6 8H18V19C18 19.5304 17.7893 20.0391 17.4142 20.4142C17.0391 20.7893 16.5304 21 16 21H8C7.46957 21 6.96086 20.7893 6.58579 20.4142C6.21071 20.0391 6 19.5304 6 19V8Z" stroke="#D4B483" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            <span>BrewBot</span>
          </div>
        </div>
      </div>
      
      <div className="content">
        <div className="chat-container">
          {listening && !isSpeaking && (
            <div className="status-indicator listening">
              <div className="listening-waves">
                <div className="wave"></div>
                <div className="wave"></div>
                <div className="wave"></div>
              </div>
              <span>Listening...</span>
            </div>
          )}
          
          {isSpeaking && (
            <div className="status-indicator speaking">
              <div className="speaking-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M11 5L6 9H2V15H6L11 19V5Z" fill="#D4B483"/>
                  <path d="M15.54 8.46C16.4774 9.39764 17.0039 10.6692 17.0039 11.995C17.0039 13.3208 16.4774 14.5924 15.54 15.53" stroke="#D4B483" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M18.07 5.93C19.9447 7.80528 20.9979 10.3447 20.9979 13C20.9979 15.6553 19.9447 18.1947 18.07 20.07" stroke="#D4B483" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
              <span>Speaking...</span>
            </div>
          )}
          
          {currentBotResponse && (
            <div className="response-box">
              <div className="response-text">{currentBotResponse}</div>
              <button className="mute-button" onClick={toggleMute}>
                {muted ? (
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M11 5L6 9H2V15H6L11 19V5Z" fill="#D4B483"/>
                    <path d="M23 9L17 15" stroke="#D4B483" strokeWidth="2" strokeLinecap="round"/>
                    <path d="M17 9L23 15" stroke="#D4B483" strokeWidth="2" strokeLinecap="round"/>
                  </svg>
                ) : (
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M11 5L6 9H2V15H6L11 19V5Z" fill="#D4B483"/>
                    <path d="M15.54 8.46C16.4774 9.39764 17.0039 10.6692 17.0039 11.995C17.0039 13.3208 16.4774 14.5924 15.54 15.53" stroke="#D4B483" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    <path d="M18.07 5.93C19.9447 7.80528 20.9979 10.3447 20.9979 13C20.9979 15.6553 19.9447 18.1947 18.07 20.07" stroke="#D4B483" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                )}
              </button>
            </div>
          )}
          
          {!isBotActive && !listening && !currentBotResponse && (
            <div className="activation-message">
              Say "coffee" to activate BrewBot
            </div>
          )}
        </div>
      </div>
      
      <div className="footer">
        <div className="footer-nav">
          <a href="#" className="footer-link">Music</a>
          <a href="#" className="footer-link">About</a>
          <a href="#" className="footer-link">Terms</a>
          <a href="#" className="footer-link">Privacy</a>
          <a href="#" className="footer-link">Contact</a>
        </div>
        <div className="copyright">© 2025 BrewBot. All rights reserved.</div>
      </div>
    </>
  );
};

export default App;
