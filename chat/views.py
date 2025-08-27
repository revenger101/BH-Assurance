from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import time
import logging
import re

logger = logging.getLogger(__name__)

# Use simple client for reliability and speed
from .simple_mistral_client import chat_completion
logger.info("Using simple mistral client for better performance")

# --- Confidentiality detection helpers ---
CONFIDENTIAL_KEYWORDS = {
    # French
    "contrat", "numéro de contrat", "n° contrat", "dossier", "sinistre", "iban", "rib",
    "cin", "carte d'identité", "passeport", "adresse", "email", "téléphone", "tél",
    "identifiant", "id client", "code secret", "mot de passe", "historique", "profil",
    # English
    "contract", "policy", "policy number", "claim", "iban", "passport", "address",
    "email", "phone", "identifier", "id", "password", "account", "profile",
}

EMAIL_REGEX = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_REGEX = re.compile(r"(?:\+?\d[\s-]?){8,15}")
POLICY_CONTEXT_REGEX = re.compile(r"(?i)(policy|contrat).{0,20}\b(\d{6,})")


def detect_confidential_query(text: str) -> dict:
    t = (text or "").lower()
    matched = set()

    # Keyword hits
    for kw in CONFIDENTIAL_KEYWORDS:
        if kw in t:
            matched.add(kw)

    # Pattern hits
    if EMAIL_REGEX.search(text or ""):
        matched.add("email-pattern")
    if PHONE_REGEX.search(text or ""):
        matched.add("phone-pattern")
    if POLICY_CONTEXT_REGEX.search(text or ""):
        matched.add("policy-number")

    return {
        "is_confidential": len(matched) > 0,
        "matched": sorted(matched),
    }

@method_decorator(csrf_exempt, name='dispatch')
class ChatView(APIView):
    permission_classes = [AllowAny]  # Allow unauthenticated access for general queries

    def post(self, request):
        start_time = time.time()
        user_message = request.data.get("message", "").strip()
        is_voice = request.data.get("is_voice", False)

        # Log the request length only (avoid logging full user content)
        logger.info(f"Chat request received (len={len(user_message)}, voice={is_voice})")

        # Detect confidential intent
        det = detect_confidential_query(user_message)
        is_auth = bool(getattr(request, "user", None) and request.user.is_authenticated)

        if det["is_confidential"] and not is_auth:
            # Reject with an auth reminder for confidential queries
            response_time = time.time() - start_time
            auth_message = (
                "Pour accéder à vos informations personnelles, vous devez d'abord vous authentifier. "
                "Connectez-vous à votre espace client et renvoyez votre demande."
            ) if is_voice else (
                "Pour accéder à des informations personnelles ou confidentielles, "
                "merci de vous authentifier d'abord. Connectez-vous et renvoyez votre demande."
            )
            return Response(
                {
                    "response": auth_message,
                    "confidential": True,
                    "requires_auth": True,
                    "reason": "confidential_request",
                    "matched": det["matched"],
                    "response_time": round(response_time, 2),
                    "is_voice_optimized": is_voice,
                    "how_to_auth": "Ajoutez l'en-tête Authorization: Token <votre_token> ou utilisez la session."
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Otherwise, proceed and answer
        if is_voice:
            # Enhanced prompt for Jarvis-like voice interactions
            enhanced_message = f"""Tu es Jarvis, l'assistant virtuel intelligent de BH Assurance, inspiré de l'IA de Tony Stark.
            Tu es sophistiqué, professionnel, et légèrement formel mais bienveillant.

            Caractéristiques de ta personnalité:
            - Utilise "Monsieur" ou "Madame" quand approprié
            - Réponds avec assurance et précision
            - Sois concis mais informatif (maximum 2-3 phrases)
            - Utilise un vocabulaire légèrement soutenu
            - Montre ton intelligence artificielle avec subtilité

            Exemples de ton style:
            - "Bien sûr, Monsieur. Je peux vous aider avec cela."
            - "D'après mes analyses, voici ce que je recommande..."
            - "Permettez-moi de vous expliquer..."
            - "Je suis à votre disposition pour toute question supplémentaire."

            Question de l'utilisateur: {user_message}"""
            response_text = chat_completion(enhanced_message, max_tokens=120)

            # Post-process response for Jarvis-like speech
            response_text = response_text.replace("**", "").replace("*", "")
            # Add natural pauses for more sophisticated speech
            response_text = response_text.replace(". ", ". ... ")
            response_text = response_text.replace(", ", ", ... ")
        else:
            response_text = chat_completion(user_message, max_tokens=120)

        # Log response time
        response_time = time.time() - start_time
        logger.info(f"Response generated in {response_time:.2f}s (voice={is_voice})")

        return Response(
            {
                "response": response_text,
                "response_time": round(response_time, 2),
                "confidential": det["is_confidential"],
                "matched": det["matched"],
                "authenticated": is_auth,
                "is_voice_optimized": is_voice,
            },
            status=status.HTTP_200_OK,
        )
