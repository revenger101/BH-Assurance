
# Add this to your chat/simple_mistral_client.py

from .client_lookup_service import ClientLookupService

# Initialize client lookup service
client_lookup = ClientLookupService()

def enhanced_chat_completion(message, max_tokens=150):
    """Enhanced chat completion with client data lookup"""
    
    # First, try client lookup
    client_info = client_lookup.search_client(message)
    
    if client_info:
        # Found client information
        return client_info
    else:
        # Fall back to regular AI model
        return chat_completion(message, max_tokens)
