import React, { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { useNavigate, Link } from "react-router-dom";
import { UserPlus, Eye, EyeOff, ArrowLeft, Check } from "lucide-react";
import "./Login.css"; // Reusing the same styles

const Signup = () => {
  const { signUp } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ 
    name: "", 
    email: "", 
    phone_number: "", 
    password: "", 
    password_confirm: "" 
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [success, setSuccess] = useState(false);

  const onChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const validateForm = () => {
    if (form.password !== form.password_confirm) {
      setError("Les mots de passe ne correspondent pas.");
      return false;
    }
    if (form.password.length < 8) {
      setError("Le mot de passe doit contenir au moins 8 caractères.");
      return false;
    }
    return true;
  };

  const onSubmit = async (e) => {
    e.preventDefault();
    setError(""); 
    
    if (!validateForm()) return;
    
    setSubmitting(true);
    try {
      await signUp({ ...form, user_type: "CLIENT" });
      setSuccess(true);
      setTimeout(() => {
        navigate("/login");
      }, 2000);
    } catch (error) {
      console.error('Signup error:', error.response?.data);

      // Handle specific validation errors
      if (error.response?.data?.errors) {
        const errors = error.response.data.errors;
        const errorMessages = [];

        Object.keys(errors).forEach(field => {
          if (Array.isArray(errors[field])) {
            errorMessages.push(...errors[field]);
          } else {
            errorMessages.push(errors[field]);
          }
        });

        setError(errorMessages.join(' '));
      } else {
        setError(error?.response?.data?.message || "Échec d'inscription. Vérifiez les informations.");
      }
    } finally {
      setSubmitting(false);
    }
  };

  if (success) {
    return (
      <div className="login-page">
        <div className="auth-main">
          <div className="container">
            <div className="auth-container" style={{ gridTemplateColumns: '1fr', justifyItems: 'center' }}>
              <div className="auth-card" style={{ maxWidth: '500px', textAlign: 'center' }}>
                <div className="auth-icon" style={{ background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)' }}>
                  <Check size={32} />
                </div>
                <h1 style={{ color: '#10b981', marginBottom: '1rem' }}>Compte créé avec succès !</h1>
                <p style={{ color: '#64748b', marginBottom: '2rem' }}>
                  Votre compte AgentBH a été créé. Vous allez être redirigé vers la page de connexion.
                </p>
                <div className="loading-spinner" style={{ 
                  width: '40px', 
                  height: '40px', 
                  border: '4px solid #e2e8f0', 
                  borderTop: '4px solid #10b981', 
                  borderRadius: '50%', 
                  animation: 'spin 1s linear infinite',
                  margin: '0 auto'
                }}></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="login-page">
      {/* Header */}
      <header className="auth-header">
        <div className="container">
          <div className="auth-header-content">
            <Link to="/" className="back-link">
              <ArrowLeft size={20} />
              Retour à l'accueil
            </Link>
            <div className="logo">
              <h1>AgentBH</h1>
              <span>Votre Assurance Digitale</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="auth-main">
        <div className="container">
          <div className="auth-container">
            <div className="auth-card">
              <div className="auth-header-section">
                <div className="auth-icon">
                  <UserPlus size={32} />
                </div>
                <h1>Créer un compte</h1>
                <p>Rejoignez AgentBH et découvrez l'avenir de la banque</p>
              </div>

              <form onSubmit={onSubmit} className="auth-form">
                <div className="form-group">
                  <label htmlFor="name">Nom complet</label>
                  <input
                    id="name"
                    name="name"
                    type="text"
                    value={form.name}
                    onChange={onChange}
                    required
                    className="form-input"
                    placeholder="Ex: Jean Dupont, Mary O'Connor, John Smith Jr."
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="email">Adresse email</label>
                  <input
                    id="email"
                    name="email"
                    type="email"
                    value={form.email}
                    onChange={onChange}
                    required
                    className="form-input"
                    placeholder="votre@email.com"
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="phone_number">Téléphone (optionnel)</label>
                  <input
                    id="phone_number"
                    name="phone_number"
                    type="tel"
                    value={form.phone_number}
                    onChange={onChange}
                    className="form-input"
                    placeholder="+216 XX XXX XXX"
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="password">Mot de passe</label>
                  <div className="password-input-container">
                    <input
                      id="password"
                      name="password"
                      type={showPassword ? "text" : "password"}
                      value={form.password}
                      onChange={onChange}
                      required
                      className="form-input"
                      placeholder="Minimum 8 caractères"
                    />
                    <button
                      type="button"
                      className="password-toggle"
                      onClick={() => setShowPassword(!showPassword)}
                    >
                      {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                    </button>
                  </div>
                </div>

                <div className="form-group">
                  <label htmlFor="password_confirm">Confirmer le mot de passe</label>
                  <div className="password-input-container">
                    <input
                      id="password_confirm"
                      name="password_confirm"
                      type={showConfirmPassword ? "text" : "password"}
                      value={form.password_confirm}
                      onChange={onChange}
                      required
                      className="form-input"
                      placeholder="Confirmer Le MotDePasse"
                    />
                    <button
                      type="button"
                      className="password-toggle"
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    >
                      {showConfirmPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                    </button>
                  </div>
                </div>

                {error && (
                  <div className="error-message">
                    {error}
                  </div>
                )}

                <button 
                  type="submit" 
                  className="auth-submit-btn"
                  disabled={submitting}
                >
                  {submitting ? "Création en cours..." : "Créer mon compte"}
                </button>
              </form>

              <div className="auth-footer">
                <p>
                  Déjà un compte ? 
                  <Link to="/login" className="auth-link">
                    Se connecter
                  </Link>
                </p>
              </div>
            </div>

            <div className="auth-info">
              <h3>Avantages AgentBH</h3>
              <ul>
                <li>Inscription gratuite et rapide</li>
                <li>Assistant IA personnalisé</li>
                <li>Sécurité bancaire maximale</li>
                <li>Support client dédié</li>
                <li>Interface moderne et intuitive</li>
                <li>Services bancaires complets</li>
              </ul>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Signup;
