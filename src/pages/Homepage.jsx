import React, { useState } from 'react';
import { MessageCircle, Phone, Mail, MapPin, ChevronRight, Users, Shield, TrendingUp, Award, LogOut } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { Link } from 'react-router-dom';
import QuoteCard from '../components/QuoteCard';
import './Homepage.css';

const Homepage = ({ onOpenChat, onActivateHologram, isHologramActive, onDeactivateHologram }) => {
  const { user, signOut } = useAuth();
  const [selectedService, setSelectedService] = useState('particuliers');

  const services = [
    { id: 'particuliers', label: 'Particuliers', active: true },
    { id: 'entreprises', label: 'Entreprises', active: false },
    { id: 'professionnels', label: 'Professionnels', active: false },
    { id: 'jeunes', label: 'Jeunes', active: false },
    { id: 'seniors', label: 'Seniors', active: false }
  ];

  const news = [
    {
      id: 1,
      title: "Nouveau service bancaire digital",
      description: "Découvrez nos nouvelles solutions bancaires digitales pour une expérience client optimisée.",
      date: "20 Août 2025"
    },
    {
      id: 2,
      title: "Taux préférentiels pour les jeunes",
      description: "Profitez de nos offres spéciales dédiées aux jeunes entrepreneurs et étudiants.",
      date: "18 Août 2025"
    },
    {
      id: 3,
      title: "Expansion du réseau d'agences",
      description: "Ouverture de nouvelles agences pour mieux vous servir dans toute la Tunisie.",
      date: "15 Août 2025"
    }
  ];

  const features = [
    {
      icon: <Users className="w-8 h-8" />,
      title: "Service Client 24/7",
      description: "Notre équipe est disponible pour vous accompagner à tout moment"
    },
    {
      icon: <Shield className="w-8 h-8" />,
      title: "Sécurité Maximale",
      description: "Vos données et transactions sont protégées par les dernières technologies"
    },
    {
      icon: <TrendingUp className="w-8 h-8" />,
      title: "Solutions Innovantes",
      description: "Des produits bancaires adaptés à vos besoins et à votre style de vie"
    },
    {
      icon: <Award className="w-8 h-8" />,
      title: "Excellence Reconnue",
      description: "Une banque de confiance avec plus de 50 ans d'expérience"
    }
  ];

  return (
    <div className="homepage">
      {/* Header */}
      <header className="header">
        <div className="container">
          <div className="header-content">
            <div className="logo">
              <h1>AgentBH</h1>
              <span>Votre Assurance Digitale</span>
            </div>
            <nav className="nav">
              <a href="#accueil">Accueil</a>
              <a href="#services">Services</a>
              <a href="#produits">Produits</a>
              <a href="#agences">Agences</a>
              <a href="#contact">Contact</a>
            </nav>
            <div className="header-actions">
              {!user ? (
                <>
                  <Link to="/login" className="login-btn">Connexion</Link>
                  <Link to="/signup" className="signup-btn">Inscription</Link>
                </>
              ) : (
                <div className="user-menu">
                  <span className="user-greeting">
                    Bonjour, <strong>{user?.data.name || user?.email || 'Utilisateur'}</strong>
                  </span>
                  <button className="logout-btn" onClick={signOut}>
                    <LogOut size={16} />
                    Déconnexion
                  </button>
                </div>
              )}
              <button className="chat-btn" onClick={onOpenChat}>
                <MessageCircle size={20} />
                Chat Assistant
              </button>
            </div>
          </div>
        </div>
      </header>

  {/* Hero Section */}
      <section className="hero">
        <div className="container">
          <div className="hero-content">
            <div className="hero-text">
              <h1>Vers de Nouvelles Perspectives</h1>
              <p>Découvrez une expérience d’assurance moderne avec notre assistant IA, conçu pour vous accompagner dans toutes vos démarches.</p>
              <div className="hero-actions">
                <button className="cta-primary" onClick={onOpenChat}>
                  Essayer l'Assistant IA
                </button>
                
                <button className="cta-tertiary">
                  Devenir Client
                </button>
              </div>
            </div>
            <div className="hero-image">
              {isHologramActive ? (
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '260px' }}>
                  {/* Animated Robot SVG */}
                  <svg width="180" height="180" viewBox="0 0 200 200">
                    <circle cx="100" cy="100" r="80" fill="#22304a" stroke="#3fd2ff" strokeWidth="4" />
                    <circle cx="80" cy="90" r="10" fill="#3fd2ff">
                      <animate attributeName="r" values="10;13;10" dur="1.2s" repeatCount="indefinite" />
                    </circle>
                    <circle cx="120" cy="90" r="10" fill="#3fd2ff">
                      <animate attributeName="r" values="10;13;10" dur="1.2s" repeatCount="indefinite" />
                    </circle>
                    <rect x="90" y="130" width="20" height="7" rx="3.5" fill="#3fd2ff">
                      <animate attributeName="width" values="20;28;20" dur="1.2s" repeatCount="indefinite" />
                    </rect>
                    <ellipse cx="100" cy="115" rx="18" ry="8" fill="none" stroke="#3fd2ff" strokeWidth="2" />
                  </svg>
                  <div style={{ color: '#3fd2ff', fontWeight: 'bold', marginTop: '12px', fontSize: '1.1rem' }}>Hologramme Activé</div>
                </div>
              ) : (
                <div className="hero-card">
                  <h3>Assistant IA AgentBH</h3>
                  <p>Votre conseiller personnel disponible 24h/24</p>
                  <button onClick={onOpenChat}>
                    Commencer <ChevronRight size={16} />
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* Services Section */}
      <section className="services">
        <div className="container">
          <div className="services-tabs">
            {services.map((service) => (
              <button
                key={service.id}
                className={`service-tab ${selectedService === service.id ? 'active' : ''}`}
                onClick={() => setSelectedService(service.id)}
              >
                {service.label}
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features">
        <div className="container">
          <h2>Pourquoi Choisir AgentBH ?</h2>
          <div className="features-grid">
            {features.map((feature, index) => (
              <div key={index} className="feature-card">
                <div className="feature-icon">
                  {feature.icon}
                </div>
                <h3>{feature.title}</h3>
                <p>{feature.description}</p>
              </div>
            ))}
            {/* Quote Card */}
            <QuoteCard />
          </div>
        </div>
      </section>

      {/* News Section */}
      <section className="news">
        <div className="container">
          <h2>Dernières Actualités</h2>
          <div className="news-grid">
            {news.map((item) => (
              <div key={item.id} className="news-card">
                <div className="news-date">{item.date}</div>
                <h3>{item.title}</h3>
                <p>{item.description}</p>
                <button className="news-link">
                  En savoir plus <ChevronRight size={16} />
                </button>
              </div>
            ))}
          </div>
        </div>
      </section>

  {/* Footer */}
      <footer className="footer">
        <div className="container">
          <div className="footer-content">
            <div className="footer-section">
              <h3>AgentBH</h3>
              <p>Votre partenaire d’assurance de confiance, enrichi par l’innovation de l’intelligence artificielle</p>
            </div>
            <div className="footer-section">
              <h4>Contact</h4>
              <div className="contact-info">
                <div className="contact-item">
                  <Phone size={16} />
                  <span>+216 71 126 000</span>
                </div>
                <div className="contact-item">
                  <Mail size={16} />
                  <span>contact@agentbh.tn</span>
                </div>
                <div className="contact-item">
                  <MapPin size={16} />
                  <span>Avenue Mohamed V, Tunis</span>
                </div>
              </div>
            </div>
            <div className="footer-section">
              <h4>Services</h4>
              <ul>
                <li><a href="#comptes">Comptes</a></li>
                <li><a href="#credits">Crédits</a></li>
                <li><a href="#epargne">Épargne</a></li>
                <li><a href="#assurance">Assurance</a></li>
              </ul>
            </div>
            <div className="footer-section">
              <h4>Assistant IA</h4>
              <p>Notre assistant intelligent est disponible 24h/24 pour répondre à vos questions.</p>
              <button className="footer-chat-btn" onClick={onOpenChat}>
                <MessageCircle size={16} />
                Ouvrir le Chat
              </button>
            </div>
          </div>
          <div className="footer-bottom">
            <p>&copy; 2025 AgentBH. Tous droits réservés.</p>
          </div>
        </div>
      </footer>

      {/* Floating Chat Button */}
      <button className="floating-chat" onClick={onOpenChat}>
        <MessageCircle size={24} />
      </button>

    </div>
  );
};

export default Homepage;
