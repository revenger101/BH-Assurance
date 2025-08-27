import api from "./client";

// Backend returns { success, message, data: { user, token } }
const getToken = (res) => res?.data?.data?.token || res?.data?.token;
const getUser  = (res) => res?.data?.data?.user  || res?.data?.user;

export const register = (payload) => api.post("/api/auth/register/", payload);
export const login = (email, password) => api.post("/api/auth/login/", { email, password });
export const logout = () => api.post("/api/auth/logout/");
export const getProfile = () => api.get("/api/auth/profile/");

// Chat API
export const sendChatMessage = (message) => api.post("/api/chat/", { message });

export { getToken, getUser };