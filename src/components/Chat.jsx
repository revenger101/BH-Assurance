import React, { useState, useRef, useEffect } from 'react';
import { Mic, MicOff, Send, X, Minimize2, Zap } from 'lucide-react';
import { motion } from 'framer-motion';
import { Particles } from '@tsparticles/react';
import { tsParticles } from '@tsparticles/engine';
import { loadStarsPreset } from '@tsparticles/preset-stars';
import './Chat.css';

const Chat = ({ isOpen, onClose, onMinimize, isMinimized }) => {
  const [isVoiceEnabled, setIsVoiceEnabled] = useState(true);
  const [isHologramMode, setIsHologramMode] = useState(false);
  const [inputMessage, setInputMessage] = useState('');
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'assistant',
      text: "Bonjour! Je suis votre assistant AgentBH. Comment puis-je vous aider aujourd'hui?",
      time: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
    }
  ]);
  const [speakingMessageId, setSpeakingMessageId] = useState(null);
  const messagesEndRef = useRef(null);
  const [particlesInit, setParticlesInit] = useState(false);

  useEffect(() => {
    async function initParticles() {
      await loadStarsPreset(tsParticles); // Use tsParticles instance directly
      setParticlesInit(true);
    }
    initParticles();
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = () => {
    if (!inputMessage.trim()) return;

    const newMessage = {
      id: Date.now(),
      type: 'user',
      text: inputMessage,
      time: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, newMessage]);
    setInputMessage('');

    setTimeout(() => {
      const assistantId = Date.now() + 1;
      const assistantResponse = {
        id: assistantId,
        type: 'assistant',
        text: "Merci pour votre message. Je suis là pour vous aider avec vos questions bancaires. Que souhaitez-vous savoir?",
        time: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, assistantResponse]);
      // Trigger speaking animation for 3 seconds
      setSpeakingMessageId(assistantId);
      setTimeout(() => setSpeakingMessageId(null), 3000);
    }, 1000);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const toggleHologramMode = () => {
    setIsHologramMode(!isHologramMode);
    const hologramMessage = {
      id: Date.now(),
      type: 'system',
      text: isHologramMode
        ? "Mode hologramme désactivé - Retour au chat normal"
        : "Mode hologramme activé - Expérience immersive activée",
      time: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
    };
    setMessages(prev => [...prev, hologramMessage]);
  };

  if (!isOpen) return null;

  return (
    <div className={`chat-overlay ${isMinimized ? 'minimized' : ''} ${isHologramMode ? 'hologram-mode' : ''}`}>
      <div className="chat-container">
        {isHologramMode && particlesInit && (
          <Particles
            id="tsparticles"
            className="particles-background"
            options={{
              preset: "stars",
              background: { color: { value: "transparent" } },
              particles: {
                color: { value: "#00e5ff" },
                number: { value: 50 },
                opacity: { value: 0.5 },
                size: { value: 1 },
                move: { speed: 0.5 },
              },
            }}
          />
        )}
        <div className="chat-header">
          <div className="chat-header-info">
            <div className="chat-avatar">
              <div className="avatar-circle">
                <div className="avatar-dot"></div>
              </div>
            </div>
            <div className="chat-title">
              <h3>AgentBH</h3>
              <span className="chat-status">En ligne</span>
            </div>
          </div>
          <div className="chat-controls">
            <button
              className={`control-btn hologram-btn ${isHologramMode ? 'active' : ''}`}
              onClick={toggleHologramMode}
              title={isHologramMode ? "Désactiver le mode hologramme" : "Activer le mode hologramme"}
            >
              <Zap size={18} />
            </button>
            <button
              className="control-btn"
              onClick={onMinimize}
              title="Réduire"
            >
              <Minimize2 size={18} />
            </button>
            <button
              className="control-btn"
              onClick={onClose}
              title="Fermer"
            >
              <X size={18} />
            </button>
          </div>
        </div>

        {!isMinimized && (
          <>
            <div className="chat-messages">
              {messages.length === 1 && (
                <div className="welcome-screen">
                  <div className="welcome-avatar">
                    <div className="avatar-wrapper">
                      <div className="outer-ring">
                        <div className="inner-ring">
                          <div className="core-circle">
                            <div className="center-dot"></div>
                          </div>
                        </div>
                      </div>
                      <div className="pulse-ring pulse-ring-1"></div>
                      <div className="pulse-ring pulse-ring-2"></div>
                    </div>
                  </div>
                  <div className="welcome-info">
                    <h3>AgentBH</h3>
                    <p>Votre assistant bancaire intelligent</p>
                  </div>
                </div>
              )}

              <div className="messages-list">
                {messages.map((message) => (
                  <motion.div
                    key={message.id}
                    className={`message ${message.type}-message`}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.5, ease: "easeOut" }}
                  >
                    <motion.div 
                      className="message-bubble"
                      animate={message.type === 'assistant' && speakingMessageId === message.id ? { scale: [1, 1.05, 1] } : {}}
                      transition={{ duration: 0.3, repeat: 3 }}
                    >
                      <p className="message-text">{message.text}</p>
                      <p className="message-time">{message.time}</p>
                    </motion.div>
                    {message.type === 'assistant' && speakingMessageId === message.id && (
                      <div className="speech-wave">
                        <div className="wave-bar"></div>
                        <div className="wave-bar"></div>
                        <div className="wave-bar"></div>
                        <div className="wave-bar"></div>
                      </div>
                    )}
                  </motion.div>
                ))}
                <div ref={messagesEndRef} />
              </div>
            </div>

            <div className="chat-input">
              <div className="input-wrapper">
                <button 
                  className={`voice-button ${isVoiceEnabled ? 'enabled' : ''}`}
                  onClick={() => setIsVoiceEnabled(!isVoiceEnabled)}
                  title={isVoiceEnabled ? "Désactiver le micro" : "Activer le micro"}
                >
                  {isVoiceEnabled ? <Mic size={18} /> : <MicOff size={18} />}
                </button>

                <div className="input-field-wrapper">
                  <input
                    type="text"
                    placeholder="Posez votre question..."
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyDown={handleKeyPress}
                    className="message-input"
                  />
                </div>

                <button 
                  className={`send-button ${!inputMessage.trim() ? 'disabled' : ''}`}
                  disabled={!inputMessage.trim()}
                  onClick={handleSendMessage}
                  title="Envoyer"
                >
                  <Send size={18} />
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default Chat;