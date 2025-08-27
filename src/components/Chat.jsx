import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Mic, MicOff, Send, X, Minimize2, Zap, AlertCircle, Calculator, Volume2 } from 'lucide-react';
import { motion } from 'framer-motion';
import { Particles } from '@tsparticles/react';
import { tsParticles } from '@tsparticles/engine';
import { loadStarsPreset } from '@tsparticles/preset-stars';
import { Link } from 'react-router-dom';
import { sendChatMessage, formatChatResponse, formatChatError } from '../API/chat';
import { useAuth } from '../context/AuthContext';
import './Chat.css';

const Chat = ({ isOpen, onClose, onMinimize, isMinimized }) => {
  const { user } = useAuth();
  const [isVoiceEnabled, setIsVoiceEnabled] = useState(true);
  const [isHologramMode, setIsHologramMode] = useState(false);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'assistant',
      text: user
        ? `Bonjour ${user?.data.name || 'Utilisateur'}! Je suis votre assistant AgentBH. Comment puis-je vous aider aujourd'hui?`
        : "Bonjour! Je suis votre assistant AgentBH. Comment puis-je vous aider aujourd'hui?",
      time: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
    }
  ]);
  const [speakingMessageId, setSpeakingMessageId] = useState(null);
  const messagesEndRef = useRef(null);
  const [particlesInit, setParticlesInit] = useState(false);

  // Voice interaction states
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [speechRecognition, setSpeechRecognition] = useState(null);
  const [speechSynthesis, setSpeechSynthesis] = useState(null);
  const [voiceLevel, setVoiceLevel] = useState(0);
  const [mouthAnimation, setMouthAnimation] = useState('closed');
  const [isRequestingPermission, setIsRequestingPermission] = useState(false);
  const recognitionRef = useRef(null);
  const synthRef = useRef(null);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);

  useEffect(() => {
    async function initParticles() {
      await loadStarsPreset(tsParticles); // Use tsParticles instance directly
      setParticlesInit(true);
    }
    initParticles();
  }, []);

  // Initialize speech recognition and synthesis
  useEffect(() => {
    if (typeof window !== 'undefined') {
      // Check for speech recognition support
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (SpeechRecognition) {
        console.log('🎤 Speech Recognition API available');
        const recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = true; // Enable interim results for better UX
        recognition.lang = 'fr-FR';
        recognition.maxAlternatives = 3; // Get multiple alternatives

        recognition.onstart = () => {
          console.log('Jarvis is listening...');
          setIsListening(true);
        };

        recognition.onresult = (event) => {
          const result = event.results[event.results.length - 1];
          if (result.isFinal) {
            const transcript = result[0].transcript.trim();
            console.log('Voice input received:', transcript);
            if (transcript) {
              handleVoiceInput(transcript);
            }
          }
        };

        recognition.onerror = (event) => {
          console.error('❌ Speech recognition error:', event.error);
          setIsListening(false);

          // Handle specific errors with user feedback
          switch (event.error) {
            case 'not-allowed':
              alert('🎤 Microphone access denied. Please allow microphone access in your browser settings and try again.');
              break;
            case 'no-speech':
              console.log('No speech detected, will retry...');
              if (isHologramMode && !isSpeaking) {
                setTimeout(() => {
                  try {
                    recognition.start();
                  } catch (e) {
                    console.log('Failed to restart recognition:', e.message);
                  }
                }, 2000);
              }
              break;
            case 'audio-capture':
              alert('🎤 No microphone found. Please check your microphone connection and refresh the page.');
              break;
            case 'network':
              console.log('Network error, speech recognition unavailable');
              break;
            case 'aborted':
              console.log('Speech recognition aborted');
              break;
            default:
              console.log('Speech recognition error:', event.error);
          }
        };

        recognition.onend = () => {
          console.log('Speech recognition ended');
          setIsListening(false);
        };

        recognitionRef.current = recognition;
        setSpeechRecognition(recognition);
      } else {
        console.warn('❌ Speech Recognition not supported in this browser');
        alert('🎤 Speech recognition is not supported in your browser. Please use Chrome, Edge, or Safari for voice features.');
      }

      // Initialize Speech Synthesis
      if (window.speechSynthesis) {
        synthRef.current = window.speechSynthesis;
        setSpeechSynthesis(window.speechSynthesis);
        console.log('🔊 Speech Synthesis available');
      } else {
        console.warn('❌ Speech Synthesis not supported');
      }
    }
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Debug function to check browser capabilities
  const checkBrowserCapabilities = useCallback(() => {
    console.log('🔍 Browser Capabilities Check:');
    console.log('- Speech Recognition:', !!(window.SpeechRecognition || window.webkitSpeechRecognition));
    console.log('- Speech Synthesis:', !!window.speechSynthesis);
    console.log('- Media Devices:', !!navigator.mediaDevices);
    console.log('- getUserMedia:', !!navigator.mediaDevices?.getUserMedia);
    console.log('- User Agent:', navigator.userAgent);
    console.log('- Protocol:', window.location.protocol);
    console.log('- Host:', window.location.host);
  }, []);

  // Check capabilities on mount
  useEffect(() => {
    checkBrowserCapabilities();
  }, [checkBrowserCapabilities]);

  // Handle voice input from speech recognition
  const handleVoiceInput = useCallback(async (transcript) => {
    if (!transcript.trim()) return;

    // Add user message
    const userMessage = {
      id: Date.now(),
      type: 'user',
      text: transcript,
      time: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await sendChatMessage(transcript, true); // Voice flag = true
      const formattedResponse = formatChatResponse(response);
      const assistantMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        text: formattedResponse.text,
        time: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }),
        isVoiceOptimized: formattedResponse.isVoiceOptimized
      };

      setMessages(prev => [...prev, assistantMessage]);

      // Speak the response in hologram mode
      if (isHologramMode && speechSynthesis) {
        speakText(assistantMessage.text, assistantMessage.id);
      }
    } catch (error) {
      const errorMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        text: formatChatError(error),
        time: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }, [isHologramMode, speechSynthesis]);

  // Text-to-speech with Jarvis-like voice and mouth animation
  const speakText = useCallback((text, messageId) => {
    if (!synthRef.current || isSpeaking) return;

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'fr-FR';
    utterance.rate = 0.85; // Slightly slower for more authority
    utterance.pitch = 0.8; // Lower pitch for Jarvis-like sound
    utterance.volume = 0.9;

    // Find the best voice for Jarvis-like experience
    const voices = synthRef.current.getVoices();

    // Prefer male French voices for Jarvis effect
    const jarvisVoice = voices.find(voice =>
      voice.lang.startsWith('fr') &&
      (voice.name.toLowerCase().includes('male') ||
       voice.name.toLowerCase().includes('homme') ||
       voice.name.toLowerCase().includes('thomas') ||
       voice.name.toLowerCase().includes('daniel'))
    ) || voices.find(voice => voice.lang.startsWith('fr'));

    if (jarvisVoice) {
      utterance.voice = jarvisVoice;
      console.log('Using Jarvis voice:', jarvisVoice.name);
    }

    utterance.onstart = () => {
      setIsSpeaking(true);
      setSpeakingMessageId(messageId);
      setMouthAnimation('speaking');
      console.log('Jarvis is speaking:', text.substring(0, 50) + '...');
    };

    utterance.onend = () => {
      setIsSpeaking(false);
      setSpeakingMessageId(null);
      setMouthAnimation('closed');

      // Auto-start listening after speaking in hologram mode
      if (isHologramMode && !isListening) {
        setTimeout(() => {
          if (recognitionRef.current && !isListening) {
            console.log('Auto-starting listening after speech...');
            recognitionRef.current.start();
          }
        }, 1000); // Wait 1 second after speaking
      }
    };

    utterance.onerror = (event) => {
      console.error('Speech synthesis error:', event.error);
      setIsSpeaking(false);
      setSpeakingMessageId(null);
      setMouthAnimation('closed');
    };

    synthRef.current.speak(utterance);
  }, [isSpeaking, isHologramMode, isListening]);

  // Request microphone permission
  const requestMicrophonePermission = useCallback(async () => {
    setIsRequestingPermission(true);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      console.log('🎤 Microphone permission granted');
      // Stop the stream immediately as we only needed permission
      stream.getTracks().forEach(track => track.stop());
      setIsRequestingPermission(false);
      return true;
    } catch (error) {
      console.error('❌ Microphone permission denied:', error);
      setIsRequestingPermission(false);
      alert('🎤 Microphone access is required for voice features. Please allow microphone access and try again.');
      return false;
    }
  }, []);

  // Start/stop voice listening with Jarvis-like behavior
  const toggleVoiceListening = useCallback(async () => {
    if (!recognitionRef.current) {
      console.log('❌ Speech recognition not available');
      alert('🎤 Speech recognition is not available in your browser. Please use Chrome, Edge, or Safari.');
      return;
    }

    if (isListening) {
      console.log('🔇 Stopping voice recognition...');
      recognitionRef.current.stop();
    } else {
      console.log('🎤 Starting voice recognition...');

      // Request microphone permission first
      const hasPermission = await requestMicrophonePermission();
      if (!hasPermission) {
        return;
      }

      try {
        recognitionRef.current.start();
      } catch (error) {
        console.error('❌ Failed to start recognition:', error);

        if (error.name === 'InvalidStateError') {
          // Recognition is already running, stop and restart
          console.log('🔄 Recognition already running, restarting...');
          recognitionRef.current.stop();
          setTimeout(() => {
            try {
              recognitionRef.current.start();
            } catch (e) {
              console.error('❌ Failed to restart recognition:', e);
              alert('🎤 Unable to start voice recognition. Please refresh the page and try again.');
            }
          }, 100);
        } else {
          alert('🎤 Unable to start voice recognition. Please check your microphone and try again.');
        }
      }
    }
  }, [isListening, requestMicrophonePermission]);

  // Auto-start listening when hologram mode is active
  useEffect(() => {
    if (isHologramMode && !isSpeaking && !isListening && recognitionRef.current) {
      const autoStartTimer = setTimeout(() => {
        console.log('Auto-starting listening in hologram mode...');
        try {
          recognitionRef.current.start();
        } catch (error) {
          console.log('Auto-start failed, will retry:', error.message);
        }
      }, 2000);

      return () => clearTimeout(autoStartTimer);
    }
  }, [isHologramMode, isSpeaking, isListening]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = inputMessage.trim();
    const newMessage = {
      id: Date.now(),
      type: 'user',
      text: userMessage,
      time: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, newMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      // Call the backend chat API with voice flag if in hologram mode
      const apiResponse = await sendChatMessage(userMessage, isHologramMode);
      const formattedResponse = formatChatResponse(apiResponse);

      const assistantId = Date.now() + 1;
      const assistantResponse = {
        id: assistantId,
        type: 'assistant',
        text: formattedResponse.text,
        time: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }),
        isConfidential: formattedResponse.isConfidential,
        requiresAuth: formattedResponse.requiresAuth,
        responseTime: formattedResponse.responseTime,
        howToAuth: formattedResponse.howToAuth
      };

      setMessages(prev => [...prev, assistantResponse]);

      // Speak the response in hologram mode
      if (isHologramMode && speechSynthesis) {
        speakText(assistantResponse.text, assistantId);
      } else {
        // Trigger speaking animation for non-voice mode
        setSpeakingMessageId(assistantId);
        setTimeout(() => setSpeakingMessageId(null), 3000);
      }

    } catch (error) {
      console.error('Chat error:', error);
      const errorResponse = formatChatError(error);

      const assistantId = Date.now() + 1;
      const assistantResponse = {
        id: assistantId,
        type: 'assistant',
        text: errorResponse.text,
        time: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }),
        isError: true,
        isConfidential: errorResponse.isConfidential,
        requiresAuth: errorResponse.requiresAuth,
        howToAuth: errorResponse.howToAuth
      };

      setMessages(prev => [...prev, assistantResponse]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const toggleHologramMode = () => {
    const newMode = !isHologramMode;
    setIsHologramMode(newMode);

    const hologramMessage = {
      id: Date.now(),
      type: 'system',
      text: newMode
        ? "Mode hologramme activé - Expérience immersive activée. Cliquez sur le micro pour parler."
        : "Mode hologramme désactivé - Retour au chat normal",
      time: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
    };
    setMessages(prev => [...prev, hologramMessage]);

    // Auto-enable voice when entering hologram mode
    if (newMode) {
      setIsVoiceEnabled(true);
      // Speak welcome message and start listening
      setTimeout(() => {
        if (speechSynthesis) {
          const welcomeText = user
            ? `Bonjour ${user?.data.name || 'Utilisateur'}! BH Assurance à votre service. Comment puis-je vous aider aujourd'hui?`
            : "Bonjour! Je suis Jarvis, votre assistant virtuel. Comment puis-je vous aider aujourd'hui?";
          speakText(welcomeText);
        }
      }, 500);
    } else {
      // Stop any ongoing speech and listening
      if (synthRef.current) {
        synthRef.current.cancel();
      }
      if (recognitionRef.current && isListening) {
        recognitionRef.current.stop();
      }
      setIsSpeaking(false);
      setSpeakingMessageId(null);
      setMouthAnimation('closed');
      setIsListening(false);
    }
  };

  // Animated mouth component based on speaking state
  const AnimatedMouth = ({ isAnimated }) => {
    if (isAnimated) {
      return (
        <g>
          <ellipse cx="110" cy="145" rx="20" ry="8" fill="#3fd2ff" opacity="0.8">
            <animate attributeName="ry" values="8;12;8;10;8" dur="0.6s" repeatCount="indefinite" />
            <animate attributeName="opacity" values="0.8;1;0.8;0.9;0.8" dur="0.6s" repeatCount="indefinite" />
          </ellipse>
          <ellipse cx="110" cy="145" rx="15" ry="4" fill="#22304a">
            <animate attributeName="ry" values="4;8;4;6;4" dur="0.6s" repeatCount="indefinite" />
          </ellipse>
        </g>
      );
    } else {
      return <rect x="95" y="140" width="30" height="8" rx="4" fill="#3fd2ff" opacity="0.7" />;
    }
  };

  if (!isOpen) return null;

  return (
    <div className={`chat-overlay ${isMinimized ? 'minimized' : ''} ${isHologramMode ? 'hologram-mode' : ''} ${isSpeaking ? 'speaking' : ''}`}>
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
            <Link
              to="/quote"
              className="control-btn quote-btn"
              title="Demander un devis"
              onClick={onMinimize} // Minimize chat when navigating to quote
            >
              <Calculator size={18} />
            </Link>
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
            {isHologramMode ? (
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '260px', marginTop: '32px' }}>
                <svg width="220" height="220" viewBox="0 0 220 220">
                  <defs>
                    <radialGradient id="faceGradient" cx="50%" cy="50%" r="50%">
                      <stop offset="0%" stop-color="#3fd2ffcc" />
                      <stop offset="100%" stop-color="#22304a" />
                    </radialGradient>
                  </defs>
                  {/* Face shape */}
                  <ellipse cx="110" cy="110" rx="80" ry="95" fill="url(#faceGradient)" opacity="0.95" />
                  {/* Eyes */}
                  <circle cx="80" cy="100" r="8" fill="#3fd2ff">
                    {isSpeaking && <animate attributeName="r" values="8;10;8" dur="1s" repeatCount="indefinite" />}
                  </circle>
                  <circle cx="140" cy="100" r="8" fill="#3fd2ff">
                    {isSpeaking && <animate attributeName="r" values="8;10;8" dur="1s" repeatCount="indefinite" />}
                  </circle>
                  {/* Animated Mouth */}
                  <AnimatedMouth isAnimated={isSpeaking} />
                  {/* Cheek/circuit lines */}
                  <polyline points="90,120 85,115 80,120" stroke="#3fd2ff88" strokeWidth="2" fill="none" />
                  <polyline points="130,120 135,115 140,120" stroke="#3fd2ff88" strokeWidth="2" fill="none" />
                  {/* Forehead lines */}
                  <line x1="70" y1="60" x2="150" y2="60" stroke="#3fd2ff44" strokeWidth="3" />
                  {/* Side grid lines */}
                  <line x1="40" y1="110" x2="180" y2="110" stroke="#3fd2ff22" strokeWidth="2" />
                  {/* Dots and particles */}
                  <circle cx="110" cy="170" r="3" fill="#3fd2ff" opacity="0.7" />
                  <circle cx="60" cy="80" r="2" fill="#3fd2ff" opacity="0.5" />
                  <circle cx="160" cy="80" r="2" fill="#3fd2ff" opacity="0.5" />
                  <circle cx="110" cy="50" r="2" fill="#3fd2ff" opacity="0.5" />
                  {/* Outer glow */}
                  <ellipse cx="110" cy="110" rx="100" ry="110" fill="none" stroke="#3fd2ff44" strokeWidth="4" opacity="0.3" />
                </svg>
                <div style={{ color: '#3fd2ff', fontWeight: 'bold', marginTop: '12px', fontSize: '1.1rem' }}>
                  {isRequestingPermission ? 'Demande d\'autorisation...' :
                   isSpeaking ? 'Jarvis répond...' :
                   isListening ? 'Jarvis vous écoute...' :
                   'Jarvis - Assistant IA Activé'}
                </div>
                {(isListening || isSpeaking || isRequestingPermission) && (
                  <div style={{
                    color: isRequestingPermission ? '#ffa500' : isListening ? '#ff6b6b' : '#3fd2ff',
                    fontSize: '0.9rem',
                    marginTop: '4px',
                    opacity: 0.9,
                    fontStyle: 'italic'
                  }}>
                    {isRequestingPermission ? '🔐 Autorisation microphone...' :
                     isListening ? '🎤 Analyse vocale en cours...' :
                     '🔊 Synthèse vocale active...'}
                  </div>
                )}
                {isHologramMode && !isListening && !isSpeaking && !isRequestingPermission && (
                  <div style={{
                    color: '#3fd2ff',
                    fontSize: '0.8rem',
                    marginTop: '8px',
                    opacity: 0.7,
                    fontStyle: 'italic'
                  }}>
                    Cliquez sur le micro pour commencer une conversation
                  </div>
                )}
                <div className="chat-input" style={{ marginTop: '24px' }}>
                  <div className="input-wrapper" style={{ justifyContent: 'center' }}>
                    <button
                      className={`voice-button ${isListening ? 'listening' : ''} ${isVoiceEnabled ? 'enabled' : ''}`}
                      onClick={toggleVoiceListening}
                      disabled={isRequestingPermission}
                      title={isRequestingPermission ? "Demande d'autorisation..." :
                             isListening ? "Arrêter l'analyse vocale" : "Parler à Jarvis"}
                      style={{
                        background: isRequestingPermission ? '#ffa500' :
                                   isListening ? '#ff4444' : '#3fd2ff',
                        borderRadius: '50%',
                        width: '56px',
                        height: '56px',
                        boxShadow: isRequestingPermission ? '0 0 20px #ffa50088' :
                                   isListening ? '0 0 20px #ff444488' : '0 0 16px #3fd2ff88',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        border: 'none',
                        transform: isRequestingPermission ? 'scale(1.05)' :
                                   isListening ? 'scale(1.1)' : 'scale(1)',
                        transition: 'all 0.3s ease',
                        opacity: isRequestingPermission ? 0.8 : 1,
                        cursor: isRequestingPermission ? 'wait' : 'pointer'
                      }}
                    >
                      {isListening ? (
                        <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
                          <circle cx="16" cy="16" r="14" fill="#22304a" stroke="#ff4444" strokeWidth="2" />
                          <rect x="13" y="8" width="6" height="12" rx="3" fill="#ff4444" />
                          <rect x="14.5" y="20" width="3" height="5" rx="1.5" fill="#ff4444" />
                          <circle cx="16" cy="16" r="10" fill="none" stroke="#ff4444" strokeWidth="1" opacity="0.6">
                            <animate attributeName="r" values="10;14;10" dur="0.8s" repeatCount="indefinite" />
                            <animate attributeName="opacity" values="0.6;0.2;0.6" dur="0.8s" repeatCount="indefinite" />
                          </circle>
                          <circle cx="16" cy="16" r="6" fill="none" stroke="#ff4444" strokeWidth="1" opacity="0.4">
                            <animate attributeName="r" values="6;10;6" dur="1.2s" repeatCount="indefinite" />
                            <animate attributeName="opacity" values="0.4;0.1;0.4" dur="1.2s" repeatCount="indefinite" />
                          </circle>
                        </svg>
                      ) : (
                        <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
                          <circle cx="16" cy="16" r="14" fill="#22304a" stroke="#3fd2ff" strokeWidth="2" />
                          <rect x="13" y="8" width="6" height="12" rx="3" fill="#3fd2ff" />
                          <rect x="14.5" y="20" width="3" height="5" rx="1.5" fill="#3fd2ff" />
                          <ellipse cx="16" cy="27" rx="5" ry="2" fill="#3fd2ff44">
                            <animate attributeName="rx" values="5;7;5" dur="1.2s" repeatCount="indefinite" />
                          </ellipse>
                          <circle cx="16" cy="16" r="14" stroke="#3fd2ff" strokeWidth="2" opacity="0.2">
                            <animate attributeName="r" values="14;16;14" dur="1.2s" repeatCount="indefinite" />
                          </circle>
                        </svg>
                      )}
                    </button>
                  </div>
                </div>
              </div>
            ) : (
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
                        className={`message ${message.type}-message ${message.isError ? 'error-message' : ''} ${message.isConfidential ? 'confidential-message' : ''}`}
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ duration: 0.5, ease: "easeOut" }}
                      >
                        <motion.div
                          className="message-bubble"
                          animate={message.type === 'assistant' && speakingMessageId === message.id ? { scale: [1, 1.05, 1] } : {}}
                          transition={{ duration: 0.3, repeat: 3 }}
                        >
                          {message.isError && (
                            <div className="message-icon error-icon">
                              <AlertCircle size={16} />
                            </div>
                          )}
                          {message.requiresAuth && (
                            <div className="auth-required-badge">
                              🔒 Authentification requise
                            </div>
                          )}
                          <p className="message-text">{message.text}</p>
                          {message.howToAuth && (
                            <p className="auth-help-text">
                              💡 {message.howToAuth}
                            </p>
                          )}
                          <div className="message-footer">
                            <p className="message-time">{message.time}</p>
                            {message.responseTime && (
                              <span className="response-time">⚡ {message.responseTime}s</span>
                            )}
                          </div>
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

                    {/* Loading indicator */}
                    {isLoading && (
                      <motion.div
                        className="message assistant-message loading-message"
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ duration: 0.3 }}
                      >
                        <div className="message-bubble">
                          <div className="typing-indicator">
                            <div className="typing-dot"></div>
                            <div className="typing-dot"></div>
                            <div className="typing-dot"></div>
                          </div>
                          <p className="message-time">En cours...</p>
                        </div>
                      </motion.div>
                    )}

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
                      className={`send-button ${!inputMessage.trim() || isLoading ? 'disabled' : ''}`}
                      disabled={!inputMessage.trim() || isLoading}
                      onClick={handleSendMessage}
                      title={isLoading ? "Envoi en cours..." : "Envoyer"}
                    >
                      {isLoading ? (
                        <div className="loading-spinner">
                          <div className="spinner"></div>
                        </div>
                      ) : (
                        <Send size={18} />
                      )}
                    </button>
                  </div>
                </div>
              </>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default Chat;