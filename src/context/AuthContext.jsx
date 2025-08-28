import React, { createContext, useContext, useEffect, useState } from "react";
import { login as apiLogin, logout as apiLogout, getProfile, register as apiRegister, getToken, getUser } from "../API/auth";

const AuthContext = createContext(null);
export const useAuth = () => useContext(AuthContext);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(localStorage.getItem("authToken") || "");
  const [user, setUser] = useState(() => {
    try { return JSON.parse(localStorage.getItem("authUser") || "null"); } catch { return null; }
  });
  const [loading, setLoading] = useState(!!token);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    (async () => {
      if (!token) { setLoading(false); return; }
      try {
        const res = await getProfile();
        if (!active) return;
        setUser(res.data);
        localStorage.setItem("authUser", JSON.stringify(res.data));
      } catch {
        localStorage.removeItem("authToken");
        localStorage.removeItem("authUser");
        setToken("");
        setUser(null);
      } finally {
        if (active) setLoading(false);
      }
    })();
    return () => { active = false; };
  }, [token]);

  const signIn = async (email, password) => {
    setError("");
    const res = await apiLogin(email, password);
    const t = getToken(res);
    const u = getUser(res);
    if (!t) throw new Error("Token manquant.");
    setToken(t);
    localStorage.setItem("authToken", t);
    if (u) {
      setUser(u);
      localStorage.setItem("authUser", JSON.stringify(u));
    } else {
      const p = await getProfile();
      setUser(p.data);
      localStorage.setItem("authUser", JSON.stringify(p.data));
    }
  };

  const signUp = async ({ email, name, phone_number = "", user_type = "CLIENT", password, password_confirm }) => {
    setError("");
    await apiRegister({ email, name, phone_number, user_type, password, password_confirm });
  };

  const signOut = async () => {
    try { await apiLogout(); } catch {}
    localStorage.removeItem("authToken");
    localStorage.removeItem("authUser");
    setToken("");
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ token, user, loading, error, signIn, signUp, signOut }}>
      {children}
    </AuthContext.Provider>
  );
}