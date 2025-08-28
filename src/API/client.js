import axios from "axios";

const apiBase = process.env.REACT_APP_API_BASE_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: apiBase,
  headers: { "Content-Type": "application/json" },
  withCredentials: true, // Enable cookies/session handling
});

// Attach token automatically
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("authToken");
  if (token) config.headers.Authorization = `Token ${token}`;
  return config;
});

export default api;