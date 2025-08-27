import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Calculator, 
  Shield, 
  User, 
  DollarSign, 
  Calendar, 
  Cigarette,
  CheckCircle,
  AlertCircle,
  ArrowRight,
  RefreshCw,
  Lock
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { 
  sendQuoteMessage, 
  resetQuoteFlow, 
  formatQuoteResponse, 
  formatQuoteError,
  validateQuoteInput 
} from '../API/quotes';
import './Quote.css';

const Quote = () => {
  const { user } = useAuth();
  const [currentStep, setCurrentStep] = useState(0);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [flowComplete, setFlowComplete] = useState(false);
  const [devis, setDevis] = useState(null);
  const [collected, setCollected] = useState({});
  const [currentQuestion, setCurrentQuestion] = useState('');
  const [error, setError] = useState('');
  const messagesEndRef = useRef(null);

  // Dynamic steps based on product type
  const getStepsForProduct = (product) => {
    const baseSteps = [
      { key: 'produit', icon: Shield, label: 'Produit', description: 'Type d\'assurance' }
    ];

    if (product === 'auto') {
      return [
        ...baseSteps,
        { key: 'n_cin', icon: User, label: 'CIN', description: 'Numéro CIN' },
        { key: 'valeur_venale', icon: DollarSign, label: 'Valeur', description: 'Valeur vénale' },
        { key: 'nature_contrat', icon: Shield, label: 'Contrat', description: 'Nature contrat' },
        { key: 'nombre_place', icon: User, label: 'Places', description: 'Nombre places' },
        { key: 'valeur_a_neuf', icon: DollarSign, label: 'Neuf', description: 'Valeur à neuf' },
        { key: 'date_premiere_mise_en_circulation', icon: Calendar, label: 'Date', description: 'Mise en circulation' },
        { key: 'capital_bris_de_glace', icon: Shield, label: 'Bris', description: 'Capital bris glace' },
        { key: 'capital_dommage_collision', icon: Shield, label: 'Collision', description: 'Capital collision' },
        { key: 'puissance', icon: Shield, label: 'Puissance', description: 'Puissance CV' },
        { key: 'classe', icon: Shield, label: 'Classe', description: 'Classe véhicule' }
      ];
    } else if (product === 'vie') {
      return [
        ...baseSteps,
        { key: 'age', icon: User, label: 'Âge', description: 'Votre âge' },
        { key: 'capital', icon: DollarSign, label: 'Capital', description: 'Montant à assurer' },
        { key: 'duree', icon: Calendar, label: 'Durée', description: 'Période d\'assurance' },
        { key: 'fumeur', icon: Cigarette, label: 'Fumeur', description: 'Statut fumeur' }
      ];
    } else if (product === 'sante') {
      return [
        ...baseSteps,
        { key: 'age', icon: User, label: 'Âge', description: 'Votre âge' },
        { key: 'capital', icon: DollarSign, label: 'Capital', description: 'Capital santé' }
      ];
    } else if (product === 'habitation') {
      return [
        ...baseSteps,
        { key: 'valeur_bien', icon: DollarSign, label: 'Valeur', description: 'Valeur du bien' },
        { key: 'superficie', icon: Shield, label: 'Surface', description: 'Superficie m²' }
      ];
    }

    return baseSteps;
  };

  const selectedProduct = collected.produit;
  const steps = getStepsForProduct(selectedProduct);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Initialize the quote flow
    initializeQuote();
  }, []);

  const initializeQuote = async () => {
    setIsLoading(true);
    try {
      const response = await sendQuoteMessage('');
      const formatted = formatQuoteResponse(response);
      
      if (formatted.question) {
        setCurrentQuestion(formatted.question);
        addMessage('assistant', formatted.question);
      }
      
      setCollected(formatted.collected);
      updateCurrentStep(formatted.collected);
    } catch (error) {
      const errorFormatted = formatQuoteError(error);
      setError(errorFormatted.message);
      addMessage('error', errorFormatted.message);
    } finally {
      setIsLoading(false);
    }
  };

  const addMessage = (type, content, metadata = {}) => {
    const newMessage = {
      id: Date.now(),
      type,
      content,
      timestamp: new Date().toLocaleTimeString('fr-FR', { 
        hour: '2-digit', 
        minute: '2-digit' 
      }),
      ...metadata
    };
    setMessages(prev => [...prev, newMessage]);
  };

  const updateCurrentStep = (collectedData) => {
    const stepIndex = steps.findIndex(step => !(step.key in collectedData));
    setCurrentStep(stepIndex === -1 ? steps.length : stepIndex);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    const userInput = inputValue.trim();
    setInputValue('');
    setError('');

    // Add user message
    addMessage('user', userInput);

    // Validate input if we know the current field
    const currentField = steps[currentStep]?.key;
    if (currentField) {
      const validation = validateQuoteInput(currentField, userInput);
      if (!validation.isValid) {
        addMessage('error', validation.error);
        return;
      }
    }

    setIsLoading(true);
    try {
      const response = await sendQuoteMessage(userInput);
      const formatted = formatQuoteResponse(response);

      if (formatted.complete && formatted.devis) {
        // Quote complete
        setFlowComplete(true);
        setDevis(formatted.devis);
        addMessage('success', formatted.message || 'Voici votre devis', {
          devis: formatted.devis
        });
      } else if (formatted.requiresAuth) {
        // Authentication required
        addMessage('auth', formatted.message, {
          requiresAuth: true,
          howToAuth: formatted.howToAuth
        });
      } else if (formatted.question) {
        // Next question
        setCurrentQuestion(formatted.question);
        addMessage('assistant', formatted.question);
      }

      setCollected(formatted.collected);
      updateCurrentStep(formatted.collected);

    } catch (error) {
      const errorFormatted = formatQuoteError(error);
      if (errorFormatted.requiresAuth) {
        addMessage('auth', errorFormatted.message, {
          requiresAuth: true,
          howToAuth: errorFormatted.howToAuth,
          collected: errorFormatted.collected
        });
        setCollected(errorFormatted.collected);
        updateCurrentStep(errorFormatted.collected);
      } else {
        addMessage('error', errorFormatted.message);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = async () => {
    setIsLoading(true);
    try {
      await resetQuoteFlow();
      setMessages([]);
      setCurrentStep(0);
      setFlowComplete(false);
      setDevis(null);
      setCollected({});
      setCurrentQuestion('');
      setError('');
      
      // Reinitialize
      await initializeQuote();
    } catch (error) {
      console.error('Reset error:', error);
      setError('Erreur lors de la réinitialisation');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="quote-page">
      <div className="quote-container">
        {/* Header */}
        <div className="quote-header">
          <div className="header-content">
            <div className="header-icon">
              <Calculator size={32} />
            </div>
            <div className="header-text">
              <h1>Demande de Devis</h1>
              <p>Obtenez votre devis d'assurance personnalisé en quelques minutes</p>
            </div>
          </div>
          
          {!flowComplete && (
            <div className="progress-bar">
              <div className="progress-steps">
                {steps.map((step, index) => {
                  const Icon = step.icon;
                  const isCompleted = index < currentStep;
                  const isCurrent = index === currentStep;
                  
                  return (
                    <div 
                      key={step.key}
                      className={`progress-step ${isCompleted ? 'completed' : ''} ${isCurrent ? 'current' : ''}`}
                    >
                      <div className="step-icon">
                        {isCompleted ? <CheckCircle size={20} /> : <Icon size={20} />}
                      </div>
                      <div className="step-info">
                        <span className="step-label">{step.label}</span>
                        <span className="step-description">{step.description}</span>
                      </div>
                    </div>
                  );
                })}
              </div>
              <div className="progress-line">
                <div 
                  className="progress-fill"
                  style={{ width: `${(currentStep / steps.length) * 100}%` }}
                />
              </div>
            </div>
          )}
        </div>

        {/* Messages */}
        <div className="quote-messages">
          <AnimatePresence>
            {messages.map((message) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className={`message ${message.type}-message`}
              >
                <div className="message-content">
                  {message.type === 'error' && <AlertCircle size={16} />}
                  {message.type === 'success' && <CheckCircle size={16} />}
                  {message.type === 'auth' && <Lock size={16} />}
                  
                  <div className="message-text">
                    {message.content}
                    
                    {message.devis && (
                      <div className="devis-summary">
                        <h3>📋 Votre Devis {message.devis.produit}</h3>

                        {message.devis.source === 'api_externe' && message.devis.api_response ? (
                          // Real API response for auto insurance
                          <div className="devis-details">
                            <div className="api-badge">
                              ✅ Devis généré via API externe officielle
                            </div>
                            <div className="devis-content">
                              <h4>Réponse de l'API:</h4>
                              <pre className="api-response">
                                {JSON.stringify(message.devis.api_response, null, 2)}
                              </pre>
                            </div>
                            <div className="devis-params">
                              <h4>Paramètres utilisés:</h4>
                              {Object.entries(message.devis.parametres).map(([key, value]) => (
                                <div key={key} className="devis-row">
                                  <span>{key}:</span>
                                  <strong>{value}</strong>
                                </div>
                              ))}
                            </div>
                          </div>
                        ) : (
                          // Simulated or other API responses
                          <div className="devis-details">
                            {message.devis.note && (
                              <div className="devis-note">
                                ℹ️ {message.devis.note}
                              </div>
                            )}

                            {message.devis.capital && (
                              <div className="devis-row">
                                <span>Capital:</span>
                                <strong>{message.devis.capital.toLocaleString()} {message.devis.devise || 'TND'}</strong>
                              </div>
                            )}

                            {message.devis.prime_mensuelle && (
                              <div className="devis-row">
                                <span>Prime mensuelle:</span>
                                <strong className="price">{message.devis.prime_mensuelle} {message.devis.devise || 'TND'}</strong>
                              </div>
                            )}

                            {message.devis.prime_annuelle && (
                              <div className="devis-row">
                                <span>Prime annuelle:</span>
                                <strong className="price">{message.devis.prime_annuelle} {message.devis.devise || 'TND'}</strong>
                              </div>
                            )}

                            {message.devis.hypotheses && (
                              <div className="devis-hypotheses">
                                <h4>Hypothèses de calcul:</h4>
                                {Object.entries(message.devis.hypotheses).map(([key, value]) => (
                                  <div key={key} className="devis-row small">
                                    <span>{key}:</span>
                                    <span>{value}</span>
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    )}
                    
                    {message.howToAuth && (
                      <div className="auth-help">
                        💡 {message.howToAuth}
                      </div>
                    )}
                  </div>
                  
                  <span className="message-time">{message.timestamp}</span>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
          
          {isLoading && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="message assistant-message loading"
            >
              <div className="message-content">
                <div className="typing-indicator">
                  <div className="typing-dot"></div>
                  <div className="typing-dot"></div>
                  <div className="typing-dot"></div>
                </div>
                <span className="message-time">En cours...</span>
              </div>
            </motion.div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input Form */}
        {!flowComplete && (
          <form onSubmit={handleSubmit} className="quote-input-form">
            <div className="input-wrapper">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder={currentQuestion ? "Votre réponse..." : "Tapez votre message..."}
                disabled={isLoading}
                className="quote-input"
              />
              <button 
                type="submit" 
                disabled={!inputValue.trim() || isLoading}
                className="submit-button"
              >
                {isLoading ? (
                  <RefreshCw size={20} className="spinning" />
                ) : (
                  <ArrowRight size={20} />
                )}
              </button>
            </div>
          </form>
        )}

        {/* Reset Button */}
        <div className="quote-actions">
          <button onClick={handleReset} className="reset-button" disabled={isLoading}>
            <RefreshCw size={16} />
            Recommencer
          </button>
        </div>
      </div>
    </div>
  );
};

export default Quote;
