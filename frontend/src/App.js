import React, { useState, useRef, useEffect } from 'react';
import { Send, BookOpen, Heart, Sparkles } from 'lucide-react';
import './App.css';

function App() {
  const [messages, setMessages] = useState([
    {
      type: 'bot',
      text: 'வணக்கம்! 🙏 நான் திருக்குறள் அடிப்படையில் வாழ்க்கை ஆலோசனை வழங்கும் AI உதவியாளர். உங்கள் மனதில் என்ன இருக்கிறது என்று பகிர்ந்துகொள்ளுங்கள்.',
      tamil: true
    }
  ]);
  const [input, setInput] = useState('');
  const [language, setLanguage] = useState('tamil');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { type: 'user', text: userMessage }]);
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:5000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage,
          language: language
        })
      });

      const data = await response.json();
      
      if (data.error) {
        throw new Error(data.error);
      }

      setMessages(prev => [...prev, { 
        type: 'bot', 
        text: data.response,
        tamil: language === 'tamil',
        kurals: data.relevant_kurals
      }]);
    } catch (error) {
      setMessages(prev => [...prev, { 
        type: 'bot', 
        text: 'மன்னிக்கவும், ஏதோ பிழை ஏற்பட்டது. மீண்டும் முயற்சிக்கவும். / Sorry, something went wrong. Please try again.',
        error: true
      }]);
      console.error('Error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const quickPrompts = [
    { tamil: 'என் வாழ்க்கையில் எல்லாம் தோல்வியாக உள்ளது', english: 'Everything is failing in my life' },
    { tamil: 'என் நண்பர் என்னை விட்டு சென்றுவிட்டார்', english: 'My friend left me' },
    { tamil: 'எனக்கு கோபம் கட்டுப்படுத்த முடியவில்லை', english: 'I cannot control my anger' },
    { tamil: 'என் குடும்பத்துடன் பிரச்சனை உள்ளது', english: 'Having problems with family' },
    { tamil: 'கல்வியில் கவனமின்மை', english: 'Lack of attention to education' },
    { tamil: 'காதலில் தோல்வி', english: 'Failure in love' }
  ];

  return (
    <div className="app">
      {/* Header */}
      <header className="app-header">
        <div className="header-content">
          <div className="header-left">
            <BookOpen className="header-icon" />
            <div>
              <h3>திருக்குறள் AI ஆலோசகர்</h3>
              <p>Thirukkural Life Advice Chatbot</p>
            </div>
          </div>
          <div className="language-toggle">
            <button
              onClick={() => setLanguage('tamil')}
              className={language === 'tamil' ? 'active' : ''}
            >
              தமிழ்
            </button>
            <button
              onClick={() => setLanguage('english')}
              className={language === 'english' ? 'active' : ''}
            >
              English
            </button>
          </div>
        </div>
      </header>

      {/* Messages Area */}
      <div className="messages-container">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`message ${msg.type === 'user' ? 'user-message' : 'bot-message'} ${msg.error ? 'error-message' : ''}`}
          >
            {msg.type === 'bot' && !msg.error && (
              <div className="message-header">
                <Heart className="heart-icon" />
                <span>திருக்குறள் ஞானம்</span>
              </div>
            )}
            <p className="message-text">{msg.text}</p>
          </div>
        ))}
        
        {isLoading && (
          <div className="message bot-message loading-message">
            <div className="loading-content">
              <Sparkles className="loading-icon" />
              <span>சிந்தித்துக்கொண்டிருக்கிறேன்...</span>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Prompts */}
      {messages.length <= 1 && (
        <div className="quick-prompts">
          <p className="prompts-title">
            விரைவான கேள்விகள் / Quick prompts:
          </p>
          <div className="prompts-grid">
            {quickPrompts.map((prompt, idx) => (
              <button
                key={idx}
                onClick={() => setInput(language === 'tamil' ? prompt.tamil : prompt.english)}
                className="prompt-button"
              >
                {language === 'tamil' ? prompt.tamil : prompt.english}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input Area */}
      <div className="input-area">
        <div className="input-container">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={language === 'tamil' ? 'உங்கள் கவலையை இங்கே பகிர்ந்துகொள்ளுங்கள்...' : 'Share your concerns here...'}
            className="input-field"
            rows="2"
            disabled={isLoading}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className="send-button"
          >
            <Send className="send-icon" />
          </button>
        </div>
        <p className="footer-text">
          திருவள்ளுவர் வாழ்க்கை ஞானத்துடன் இயங்குகிறது | Powered by Thiruvalluvar's wisdom
        </p>
      </div>
    </div>
  );
}

export default App;