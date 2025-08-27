import React from 'react';
import { motion } from 'framer-motion';
import { Calculator, Shield, Clock, CheckCircle } from 'lucide-react';
import { Link } from 'react-router-dom';
import './QuoteCard.css';

const QuoteCard = () => {
  const features = [
    { icon: <Clock size={16} />, text: "Devis en 5 minutes" },
    { icon: <Shield size={16} />, text: "Tous types d'assurance" },
    { icon: <CheckCircle size={16} />, text: "Tarifs personnalisés" }
  ];

  return (
    <motion.div 
      className="quote-card"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
    >
      <div className="quote-card-header">
        <div className="quote-icon">
          <Calculator size={24} />
        </div>
        <div className="quote-title">
          <h3>Demande de Devis</h3>
          <p>Obtenez votre devis personnalisé</p>
        </div>
      </div>
      
      <div className="quote-features">
        {features.map((feature, index) => (
          <div key={index} className="quote-feature">
            <span className="feature-icon">{feature.icon}</span>
            <span className="feature-text">{feature.text}</span>
          </div>
        ))}
      </div>
      
      <div className="quote-products">
        <div className="product-tags">
          <span className="product-tag">Vie</span>
          <span className="product-tag">Auto</span>
          <span className="product-tag">Santé</span>
          <span className="product-tag">Habitation</span>
        </div>
      </div>
      
      <Link to="/quote" className="quote-cta">
        <Calculator size={18} />
        Commencer mon devis
      </Link>
    </motion.div>
  );
};

export default QuoteCard;
