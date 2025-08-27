import api from "./client";

/**
 * Send a message to the chat API
 * @param {string} message - The user's message
 * @param {boolean} isVoice - Whether this is a voice interaction
 * @returns {Promise} - API response with the assistant's reply
 */
export const sendChatMessage = async (message, isVoice = false) => {
  try {
    const response = await api.post("/api/chat/", {
      message,
      is_voice: isVoice
    });
    return response.data;
  } catch (error) {
    console.error('Chat API error:', error);
    throw error;
  }
};

/**
 * Handle chat API response and extract the assistant's message
 * @param {Object} apiResponse - Response from the chat API
 * @returns {Object} - Formatted message object
 */
export const formatChatResponse = (apiResponse) => {
  return {
    text: apiResponse.response || "Désolé, je n'ai pas pu traiter votre demande.",
    isConfidential: apiResponse.confidential || false,
    requiresAuth: apiResponse.requires_auth || false,
    responseTime: apiResponse.response_time || 0,
    reason: apiResponse.reason || null,
    matched: apiResponse.matched || [],
    howToAuth: apiResponse.how_to_auth || null,
    isVoiceOptimized: apiResponse.is_voice_optimized || false
  };
};

/**
 * Create an error message for chat failures
 * @param {Error} error - The error object
 * @returns {Object} - Formatted error message
 */
export const formatChatError = (error) => {
  if (error.response?.status === 401) {
    return {
      text: error.response.data?.response || "Authentification requise pour cette demande.",
      isConfidential: true,
      requiresAuth: true,
      isError: true,
      howToAuth: error.response.data?.how_to_auth
    };
  }
  
  if (error.response?.status === 429) {
    return {
      text: "Trop de requêtes. Veuillez patienter un moment avant de réessayer.",
      isError: true
    };
  }
  
  return {
    text: "Désolé, une erreur s'est produite. Veuillez réessayer dans quelques instants.",
    isError: true
  };
};
