import React, { useState, useRef, useEffect } from 'react';
import styles from './Chatbot.module.css';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface Source {
  text: string;
  url: string;
  title: string;
  module: string;
  section: string;
  score: number;
}

interface ChatResponse {
  response: string;
  conversation_id: string;
  sources: Source[];
  confidence_score: number;
}

const Chatbot: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [selectedText, setSelectedText] = useState('');
  const [isMinimized, setIsMinimized] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Listen for text selection events
  useEffect(() => {
    const handleTextSelection = () => {
      const selection = window.getSelection();
      if (selection && selection.toString().trim()) {
        setSelectedText(selection.toString().trim());
      }
    };

    document.addEventListener('mouseup', handleTextSelection);
    document.addEventListener('keyup', handleTextSelection);

    return () => {
      document.removeEventListener('mouseup', handleTextSelection);
      document.removeEventListener('keyup', handleTextSelection);
    };
  }, []);

  const sendMessage = async (message: string) => {
    if (!message.trim()) return;

    const userMessage: Message = {
      role: 'user',
      content: message,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message,
          conversation_id: conversationId,
          selected_text: selectedText || undefined,
          max_results: 5,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: ChatResponse = await response.json();

      setConversationId(data.conversation_id);

      const assistantMessage: Message = {
        role: 'assistant',
        content: data.response,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, assistantMessage]);

      // Clear selected text after using it
      setSelectedText('');

    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage(inputMessage);
  };

  const clearConversation = () => {
    setMessages([]);
    setConversationId(null);
    setSelectedText('');
  };

  if (isMinimized) {
    return (
      <div className={styles.chatbotMinimized}>
        <button
          className={styles.chatbotToggle}
          onClick={() => setIsMinimized(false)}
          aria-label="Open chatbot"
        >
          💬 Ask AI
        </button>
      </div>
    );
  }

  return (
    <div className={styles.chatbot}>
      <div className={styles.chatbotHeader}>
        <h3>🤖 Physical AI & Robotics Assistant</h3>
        <div className={styles.headerButtons}>
          <button
            className={styles.clearButton}
            onClick={clearConversation}
            title="Clear conversation"
          >
            🗑️
          </button>
          <button
            className={styles.minimizeButton}
            onClick={() => setIsMinimized(true)}
            title="Minimize"
          >
            −
          </button>
        </div>
      </div>

      {selectedText && (
        <div className={styles.selectedText}>
          <div className={styles.selectedTextHeader}>
            <span>📄 Selected Text Context:</span>
            <button
              className={styles.clearSelectedText}
              onClick={() => setSelectedText('')}
              title="Clear selected text"
            >
              ✕
            </button>
          </div>
          <div className={styles.selectedTextContent}>
            {selectedText.length > 100 ? `${selectedText.substring(0, 100)}...` : selectedText}
          </div>
        </div>
      )}

      <div className={styles.messages}>
        {messages.length === 0 && (
          <div className={styles.welcomeMessage}>
            <p>👋 Hi! I'm your AI assistant for the Physical AI & Humanoid Robotics course.</p>
            <p>💡 <strong>Tip:</strong> Select any text on the page to ask questions about it!</p>
            <p>📚 Ask me anything about robotics, AI, or the course content.</p>
          </div>
        )}

        {messages.map((message, index) => (
          <div
            key={index}
            className={`${styles.message} ${styles[message.role]}`}
          >
            <div className={styles.messageContent}>
              {message.content}
            </div>
            <div className={styles.messageTime}>
              {message.timestamp.toLocaleTimeString()}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className={`${styles.message} ${styles.assistant}`}>
            <div className={styles.messageContent}>
              <div className={styles.messageContent}>
                <div className={styles.typingIndicator}>
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <form className={styles.inputForm} onSubmit={handleSubmit}>
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          placeholder="Ask me about robotics, AI, or select text to ask specific questions..."
          disabled={isLoading}
          className={styles.input}
        />
        <button
          type="submit"
          disabled={isLoading || !inputMessage.trim()}
          className={styles.sendButton}
        >
          {isLoading ? '⏳' : '📤'}
        </button>
      </form>
    </div>
  );
};

export default Chatbot;