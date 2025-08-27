from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
import requests

from .flow import get_next_field, FIELDS, simulate_quote
from .models import QuoteRequest

SESSION_KEY = "quote_flow_state"

@method_decorator(csrf_exempt, name='dispatch')
class QuoteView(APIView):
    permission_classes = [AllowAny]  
    throttle_scope = 'quote'

    def post(self, request):
        """
        Body: {"message": "user answer"}
        - Maintains a simple session-based state machine for collecting required fields
        - When all fields are collected, calls external quote API if configured, otherwise simulates
        """
        state = request.session.get(SESSION_KEY) or {"collected": {}, "complete": False}
        collected = state["collected"]
        user_msg = (request.data.get("message") or "").strip()

        # Determine the next missing field
        next_field = get_next_field(collected)

        # If we are waiting for a specific field, try to parse user input for it
        if next_field and user_msg:
            value, err = next_field.parser(user_msg)
            if err:
                # Ask again the same question with error
                request.session[SESSION_KEY] = state
                request.session.modified = True
                return Response({
                    "question": f"{err} {next_field.question}",
                    "collected": collected,
                    "complete": False
                }, status=status.HTTP_200_OK)
            # Save parsed value
            collected[next_field.key] = value
            request.session[SESSION_KEY] = state
            request.session.modified = True
            # Move to next
            next_field = get_next_field(collected)

        # If there is still a missing field, ask it
        if next_field:
            request.session[SESSION_KEY] = state
            request.session.modified = True
            return Response({
                "question": next_field.question,
                "collected": collected,
                "complete": False
            }, status=status.HTTP_200_OK)

        # All data collected: require authentication to obtain the final devis
        if not (getattr(request, "user", None) and request.user.is_authenticated):
            return Response({
                "message": "Authentification requise pour obtenir un devis.",
                "requires_auth": True,
                "reason": "auth_required_for_devis",
                "collected": collected,
                "complete": False,
                "how_to_auth": "Envoyez l'en-tête Authorization: Token <votre_token> ou connectez-vous via session."
            }, status=status.HTTP_401_UNAUTHORIZED)

        # Proceed to build devis (authenticated user)
        payload = collected.copy()
        produit = payload.get("produit", "").lower()

        # Handle AUTO insurance with real API
        if produit == "auto":
            auto_api_url = "https://apidevis.onrender.com/api/auto/packs"
            try:
                # Build query parameters for the auto API
                params = {
                    "n_cin": payload.get("n_cin"),
                    "valeur_venale": payload.get("valeur_venale"),
                    "nature_contrat": payload.get("nature_contrat"),
                    "nombre_place": payload.get("nombre_place"),
                    "valeur_a_neuf": payload.get("valeur_a_neuf"),
                    "date_premiere_mise_en_circulation": payload.get("date_premiere_mise_en_circulation"),
                    "capital_bris_de_glace": payload.get("capital_bris_de_glace"),
                    "capital_dommage_collision": payload.get("capital_dommage_collision"),
                    "puissance": payload.get("puissance"),
                    "classe": payload.get("classe"),
                }

                # Make GET request to the real auto API
                r = requests.get(auto_api_url, params=params, timeout=30)
                r.raise_for_status()
                api_response = r.json()

                # Format the response for our frontend
                dev = {
                    "produit": "auto",
                    "source": "api_externe",
                    "api_response": api_response,
                    "parametres": payload,
                    "message": "Devis auto généré via API externe",
                    "api_url": auto_api_url
                }

            except Exception as e:
                # Fallback to simulated quote on API failure
                dev = simulate_quote(payload)
                dev["note"] = f"API externe indisponible, devis simulé localement. Erreur: {str(e)}"
                dev["api_error"] = str(e)
        else:
            # For other products, use local simulation or configured API
            quote_api_url = getattr(settings, "QUOTE_API_URL", None)
            if quote_api_url:
                headers = {"Content-Type": "application/json"}
                auth = request.headers.get("Authorization")
                if auth:
                    headers["Authorization"] = auth
                try:
                    r = requests.post(quote_api_url, json=payload, headers=headers, timeout=20)
                    r.raise_for_status()
                    dev = r.json()
                except Exception as e:
                    dev = simulate_quote(payload)
                    dev["note"] = f"API indisponible, devis simulé localement ({e})"
            else:
                dev = simulate_quote(payload)

        # Persist the quote request (authenticated user guaranteed)
        try:
            # Determine source
            if produit == "auto" and "api_response" in dev:
                source = 'api_externe'
            elif "note" in dev and "API indisponible" in dev["note"]:
                source = 'simulated'
            else:
                source = 'api'

            QuoteRequest.objects.create(
                user=request.user,
                produit=payload["produit"],
                collected_data=payload,
                # Legacy fields for backward compatibility
                age=payload.get("age"),
                capital=payload.get("capital", payload.get("valeur_venale")),
                duree=payload.get("duree"),
                fumeur=payload.get("fumeur"),
                devis=dev,
                source=source,
                session_key=getattr(request.session, 'session_key', ''),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                ip_address=request.META.get('REMOTE_ADDR', ''),
            )
        except Exception as e:
            # Non-fatal if persistence fails, but log it
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to persist quote request: {e}")
            pass

        # Mark flow complete and return the quote
        state["complete"] = True
        request.session[SESSION_KEY] = state
        request.session.modified = True

        return Response({
            "message": "Voici votre devis",
            "devis": dev,
            "complete": True
        }, status=status.HTTP_200_OK)

    def delete(self, request):
        """Reset the flow state"""
        if SESSION_KEY in request.session:
            del request.session[SESSION_KEY]
            request.session.modified = True
        return Response({"message": "Flux devis réinitialisé."}, status=status.HTTP_200_OK)

