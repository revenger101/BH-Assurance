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
    permission_classes = [AllowAny]  # Let anyone start the quote flow
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

        quote_api_url = getattr(settings, "QUOTE_API_URL", None)
        if quote_api_url:
            headers = {"Content-Type": "application/json"}
            # Forward auth token if present (optional)
            auth = request.headers.get("Authorization")
            if auth:
                headers["Authorization"] = auth
            try:
                r = requests.post(quote_api_url, json=payload, headers=headers, timeout=20)
                r.raise_for_status()
                dev = r.json()
            except Exception as e:
                # Fallback to simulated quote on API failure
                dev = simulate_quote(payload)
                dev["note"] = f"API indisponible, devis simulé localement ({e})"
        else:
            dev = simulate_quote(payload)

        # Persist the quote request (authenticated user guaranteed)
        try:
            QuoteRequest.objects.create(
                user=request.user,
                produit=payload["produit"],
                age=payload["age"],
                capital=payload["capital"],
                duree=payload["duree"],
                fumeur=payload["fumeur"],
                devis=dev,
                source='api' if quote_api_url else 'simulated',
                session_key=getattr(request.session, 'session_key', ''),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                ip_address=request.META.get('REMOTE_ADDR', ''),
            )
        except Exception:
            # Non-fatal if persistence fails
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

