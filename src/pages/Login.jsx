import React, { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { useNavigate, Link } from "react-router-dom";
import { MessageCircle, Eye, EyeOff, ArrowLeft } from "lucide-react";
import "./Login.css";

const Login = () => {
  const { signIn } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: "", password: "" });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  const onChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const onSubmit = async (e) => {
    e.preventDefault();
    setError(""); 
    setSubmitting(true);
    try {
      await signIn(form.email, form.password);
      navigate("/");
      
    } catch (error) {
      setError(error?.response?.data?.message || "Échec de connexion. Vérifiez vos identifiants.");
    } finally {
      setSubmitting(false);
    }
  };

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
              <span>Votre Banque Digitale</span>
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
                  <MessageCircle size={32} />
                </div>
                <h1>Se connecter</h1>
                <p>Accédez à votre espace client AgentBH</p>
              </div>

              <form onSubmit={onSubmit} className="auth-form">
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
                      placeholder="Votre mot de passe"
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
                  {submitting ? "Connexion en cours..." : "Se connecter"}
                </button>
              </form>

              <div className="auth-footer">
                <p>
                  Pas encore de compte ? 
                  <Link to="/signup" className="auth-link">
                    Créer un compte
                  </Link>
                </p>
                <Link to="/forgot-password" className="forgot-link">
                  Mot de passe oublié ?
                </Link>
              </div>
            </div>

            <div className="auth-info">
              <h3>Pourquoi choisir AgentBH ?</h3>
              <ul>
                <li>Assistant IA disponible 24h/24</li>
                <li>Sécurité bancaire de niveau professionnel</li>
                <li>Interface moderne et intuitive</li>
                <li>Support client réactif</li>
              </ul>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Login;
