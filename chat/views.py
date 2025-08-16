from rest_framework.views import APIView
from rest_framework.response import Response
from .mistral_client import chat_completion

class ChatView(APIView):
    def post(self, request):
        user_message = request.data.get("message", "")
        prompt = f"You are BH Assurance assistant.\nUser: {user_message}\nAssistant:"
        response_text = chat_completion(prompt)
        return Response({"response": response_text})
