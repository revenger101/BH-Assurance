from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import time
import logging

logger = logging.getLogger(__name__)

# Use simple client for reliability and speed
from .simple_mistral_client import chat_completion
logger.info("Using simple mistral client for better performance")

@method_decorator(csrf_exempt, name='dispatch')
class ChatView(APIView):
    permission_classes = [AllowAny]  # Allow unauthenticated access for testing

    def post(self, request):
        start_time = time.time()
        user_message = request.data.get("message", "")

        # Log the request
        logger.info(f"Chat request: {user_message[:50]}...")

        # Use optimized prompt format for your trained model
        response_text = chat_completion(user_message, max_tokens=120)

        # Log response time
        response_time = time.time() - start_time
        logger.info(f"Response generated in {response_time:.2f}s")

        return Response({
            "response": response_text,
            "response_time": round(response_time, 2)
        })
