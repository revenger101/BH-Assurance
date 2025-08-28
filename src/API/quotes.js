import api from "./client";

/**
 * Start or continue the quote flow
 * @param {string} message - User's answer to the current question
 * @returns {Promise} - API response with next question or final devis
 */
export const sendQuoteMessage = async (message = "") => {
  try {
    const response = await api.post("/api/quote/", { message });
    return response.data;
  } catch (error) {
    console.error('Quote API error:', error);
    throw error;
  }
};

/**
 * Reset the quote flow
 * @returns {Promise} - API response confirming reset
 */
export const resetQuoteFlow = async () => {
  try {
    const response = await api.delete("/api/quote/");
    return response.data;
  } catch (error) {
    console.error('Quote reset error:', error);
    throw error;
  }
};

/**
 * Format quote response for UI display
 * @param {Object} apiResponse - Response from quote API
 * @returns {Object} - Formatted response object
 */
export const formatQuoteResponse = (apiResponse) => {
  return {
    question: apiResponse.question || null,
    message: apiResponse.message || null,
    collected: apiResponse.collected || {},
    complete: apiResponse.complete || false,
    devis: apiResponse.devis || null,
    requiresAuth: apiResponse.requires_auth || false,
    reason: apiResponse.reason || null,
    howToAuth: apiResponse.how_to_auth || null
  };
};

/**
 * Format quote error for UI display
 * @param {Error} error - The error object
 * @returns {Object} - Formatted error object
 */
export const formatQuoteError = (error) => {
  if (error.response?.status === 401) {
    return {
      message: error.response.data?.message || "Authentification requise pour obtenir un devis.",
      requiresAuth: true,
      reason: error.response.data?.reason || "auth_required",
      howToAuth: error.response.data?.how_to_auth,
      collected: error.response.data?.collected || {},
      isError: true
    };
  }
  
  if (error.response?.status === 429) {
    return {
      message: "Trop de demandes de devis. Veuillez patienter un moment.",
      isError: true
    };
  }
  
  return {
    message: "Une erreur s'est produite lors de la génération du devis. Veuillez réessayer.",
    isError: true
  };
};

/**
 * Validate user input based on field type
 * @param {string} fieldKey - The field being validated
 * @param {string} value - User input value
 * @returns {Object} - Validation result {isValid, error}
 */
export const validateQuoteInput = (fieldKey, value) => {
  const trimmedValue = value.trim();

  switch (fieldKey) {
    case 'produit':
      const validProducts = ['vie', 'auto', 'sante', 'habitation'];
      const normalizedValue = trimmedValue.toLowerCase();
      if (!validProducts.includes(normalizedValue) && normalizedValue !== 'santé') {
        return {
          isValid: false,
          error: `Produit invalide. Choisissez parmi: ${validProducts.join(', ')}`
        };
      }
      return { isValid: true };

    // AUTO INSURANCE FIELDS
    case 'n_cin':
      const cin = trimmedValue.replace(/[^0-9]/g, '');
      if (cin.length !== 8) {
        return {
          isValid: false,
          error: "Le numéro CIN doit contenir exactement 8 chiffres"
        };
      }
      return { isValid: true };

    case 'valeur_venale':
    case 'valeur_a_neuf':
    case 'capital_dommage_collision':
      const valeur = parseInt(trimmedValue.replace(/[^0-9]/g, ''));
      if (isNaN(valeur) || valeur < 1000 || valeur > 500000) {
        return {
          isValid: false,
          error: "La valeur doit être entre 1,000 et 500,000 TND"
        };
      }
      return { isValid: true };

    case 'nature_contrat':
      const nature = trimmedValue.toLowerCase();
      if (!['r', 'n', 'renouvellement', 'nouveau'].includes(nature)) {
        return {
          isValid: false,
          error: "Nature du contrat: 'r' pour renouvellement, 'n' pour nouveau"
        };
      }
      return { isValid: true };

    case 'nombre_place':
      const places = parseInt(trimmedValue);
      if (isNaN(places) || places < 2 || places > 9) {
        return {
          isValid: false,
          error: "Le nombre de places doit être entre 2 et 9"
        };
      }
      return { isValid: true };

    case 'date_premiere_mise_en_circulation':
      const dateRegex = /^\d{4}-\d{2}-\d{2}$|^\d{2}\/\d{2}\/\d{4}$|^\d{2}-\d{2}-\d{4}$/;
      if (!dateRegex.test(trimmedValue)) {
        return {
          isValid: false,
          error: "Format de date: YYYY-MM-DD, DD/MM/YYYY, ou DD-MM-YYYY"
        };
      }
      return { isValid: true };

    case 'capital_bris_de_glace':
      const bris = parseInt(trimmedValue.replace(/[^0-9]/g, ''));
      if (isNaN(bris) || bris < 100 || bris > 5000) {
        return {
          isValid: false,
          error: "Le capital bris de glace doit être entre 100 et 5,000 TND"
        };
      }
      return { isValid: true };

    case 'puissance':
      const puissance = parseInt(trimmedValue);
      if (isNaN(puissance) || puissance < 3 || puissance > 20) {
        return {
          isValid: false,
          error: "La puissance doit être entre 3 et 20 CV"
        };
      }
      return { isValid: true };

    case 'classe':
      const classe = parseInt(trimmedValue);
      if (isNaN(classe) || classe < 1 || classe > 5) {
        return {
          isValid: false,
          error: "La classe doit être entre 1 et 5"
        };
      }
      return { isValid: true };

    // LIFE INSURANCE FIELDS
    case 'age':
      const age = parseInt(trimmedValue);
      if (isNaN(age) || age < 18 || age > 80) {
        return {
          isValid: false,
          error: "L'âge doit être entre 18 et 80 ans"
        };
      }
      return { isValid: true };

    case 'capital':
      const capital = parseInt(trimmedValue.replace(/[^0-9]/g, ''));
      if (isNaN(capital) || capital < 1000 || capital > 1000000) {
        return {
          isValid: false,
          error: "Le capital doit être entre 1,000 et 1,000,000 TND"
        };
      }
      return { isValid: true };

    case 'duree':
      const duree = parseInt(trimmedValue);
      if (isNaN(duree) || duree < 1 || duree > 40) {
        return {
          isValid: false,
          error: "La durée doit être entre 1 et 40 années"
        };
      }
      return { isValid: true };

    case 'fumeur':
      const normalizedFumeur = trimmedValue.toLowerCase();
      if (!['oui', 'non', 'o', 'n', 'yes', 'no', 'y'].includes(normalizedFumeur)) {
        return {
          isValid: false,
          error: "Répondez par 'oui' ou 'non'"
        };
      }
      return { isValid: true };

    // HOME INSURANCE FIELDS
    case 'valeur_bien':
      const valeurBien = parseInt(trimmedValue.replace(/[^0-9]/g, ''));
      if (isNaN(valeurBien) || valeurBien < 10000 || valeurBien > 2000000) {
        return {
          isValid: false,
          error: "La valeur du bien doit être entre 10,000 et 2,000,000 TND"
        };
      }
      return { isValid: true };

    case 'superficie':
      const superficie = parseInt(trimmedValue);
      if (isNaN(superficie) || superficie < 20 || superficie > 1000) {
        return {
          isValid: false,
          error: "La superficie doit être entre 20 et 1,000 m²"
        };
      }
      return { isValid: true };

    default:
      return { isValid: true };
  }
};
