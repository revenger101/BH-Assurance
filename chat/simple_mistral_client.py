"""
Simple Mistral Client - Reliable and Fast

This is a simplified version that prioritizes reliability and speed
over using the trained model. Use this if the main client has issues.
"""

from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Model configuration
BASE_MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.1"

# Global variables for model caching
_tokenizer = None
_model = None
_model_loaded = False

def load_simple_model():
    """Load base model with simple, reliable configuration"""
    global _tokenizer, _model, _model_loaded
    
    if _model_loaded:
        return _tokenizer, _model
    
    logger.info("🚀 Loading base Mistral model (simple mode)...")
    start_time = time.time()
    
    try:
        # Load tokenizer
        _tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_NAME)
        if _tokenizer.pad_token is None:
            _tokenizer.pad_token = _tokenizer.eos_token
        
        # Load model with simple configuration
        _model = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL_NAME,
            torch_dtype=torch.float16,
            device_map="auto",
            low_cpu_mem_usage=True
        )
        
        _model.eval()
        _model_loaded = True
        
        load_time = time.time() - start_time
        logger.info(f"✅ Base model loaded in {load_time:.2f} seconds")
        
        return _tokenizer, _model
        
    except Exception as e:
        logger.error(f"❌ Error loading model: {e}")
        raise e

def simple_chat_completion(prompt, max_tokens=60, temperature=0.6):
    """Simple, fast chat completion"""
    start_time = time.time()
    
    try:
        # Load model if needed
        tokenizer, model = load_simple_model()
        
        # Format prompt for insurance context
        formatted_prompt = f"""Tu es un assistant spécialisé en assurance. Réponds de manière concise et professionnelle.

Question: {prompt}
Réponse:"""
        
        # Tokenize with speed optimizations
        inputs = tokenizer(
            formatted_prompt,
            return_tensors="pt",
            truncation=True,
            max_length=150,  # Even shorter for speed
            padding=False
        )
        
        # Move to device
        if torch.cuda.is_available():
            inputs = {k: v.to(model.device) for k, v in inputs.items()}
        
        # Generate with speed settings
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                do_sample=True,
                temperature=temperature,
                top_p=0.9,
                top_k=30,  # Reduced for speed
                repetition_penalty=1.1,
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id,
                use_cache=True,
                num_beams=1
            )
        
        # Decode response
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract only the response part
        if "Réponse:" in response:
            response = response.split("Réponse:")[-1].strip()
        elif formatted_prompt in response:
            response = response.replace(formatted_prompt, "").strip()
        
        # Clean up response
        response = response.strip()
        if not response:
            response = "Je suis désolé, je n'ai pas pu générer une réponse appropriée."
        
        generation_time = time.time() - start_time
        logger.info(f"⚡ Response generated in {generation_time:.2f} seconds")
        
        return response
        
    except Exception as e:
        logger.error(f"❌ Error in chat completion: {e}")
        return "Je suis désolé, une erreur s'est produite. Veuillez réessayer."

# Response cache for speed
_response_cache = {}
_cache_max_size = 50

def cached_chat_completion(prompt, max_tokens=60, temperature=0.6):
    """Chat completion with response caching"""
    # Create cache key
    cache_key = hash(prompt.strip().lower())
    
    # Check cache first
    if cache_key in _response_cache:
        logger.info("⚡ Cache hit - instant response!")
        return _response_cache[cache_key]
    
    # Generate new response
    response = simple_chat_completion(prompt, max_tokens, temperature)
    
    # Cache the response
    if len(_response_cache) >= _cache_max_size:
        # Remove oldest entry
        oldest_key = next(iter(_response_cache))
        del _response_cache[oldest_key]
    
    _response_cache[cache_key] = response
    
    return response

# Main function for compatibility
def chat_completion(prompt, max_tokens=60, temperature=0.6):
    """Main chat completion function with caching"""
    return cached_chat_completion(prompt, max_tokens, temperature)

# Test function
def test_simple_client():
    """Test the simple client"""
    print("🧪 Testing Simple Mistral Client")
    print("=" * 40)
    
    test_questions = [
        "Bonjour",
        "Qu'est-ce que l'assurance vie?",
        "Comment choisir une assurance auto?"
    ]
    
    for question in test_questions:
        print(f"\n📝 Question: {question}")
        start_time = time.time()
        response = chat_completion(question)
        total_time = time.time() - start_time
        print(f"💬 Response: {response}")
        print(f"⏱️ Time: {total_time:.2f}s")

if __name__ == "__main__":
    test_simple_client()
