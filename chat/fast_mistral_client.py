"""
Fast Mistral Client - Optimized for Speed

This module provides ultra-fast inference for the BH Assurance chat system
with multiple speed optimizations.
"""

from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import torch
import time
import logging
from functools import lru_cache
import threading
import queue

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FastMistralClient:
    def __init__(self):
        self.base_model_name = "mistralai/Mistral-7B-Instruct-v0.1"
        self.trained_model_path = "bhagent/outputs/sft_mistral_combined/checkpoint-882"
        self.tokenizer = None
        self.model = None
        self.model_loaded = False
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Speed optimization settings
        self.max_input_length = 256  # Reduced for speed
        self.max_new_tokens = 100    # Reduced for speed
        self.temperature = 0.7
        self.top_p = 0.9
        self.top_k = 40
        
        # Response cache
        self.response_cache = {}
        self.cache_size = 50
        
    def load_model(self):
        """Load model with maximum speed optimizations"""
        if self.model_loaded:
            return
        
        logger.info("🚀 Loading model with speed optimizations...")
        start_time = time.time()
        
        try:
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(self.base_model_name)
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load base model with aggressive optimizations
            self.model = AutoModelForCausalLM.from_pretrained(
                self.base_model_name,
                torch_dtype=torch.float16,
                device_map="auto",
                low_cpu_mem_usage=True,
                trust_remote_code=True,
                offload_folder="bhagent/outputs/offload"
            )
            
            # Load trained adapters
            self.model = PeftModel.from_pretrained(self.model, self.trained_model_path)
            
            # Optimization: Set to eval mode and enable optimizations
            self.model.eval()
            
            # Enable torch optimizations
            if hasattr(torch, 'compile') and torch.cuda.is_available():
                try:
                    self.model = torch.compile(self.model, mode="reduce-overhead")
                    logger.info("✅ Torch compile optimization enabled")
                except:
                    logger.info("⚠️ Torch compile not available, using standard optimization")
            
            self.model_loaded = True
            load_time = time.time() - start_time
            logger.info(f"✅ Model loaded in {load_time:.2f} seconds")
            
        except Exception as e:
            logger.error(f"❌ Error loading trained model: {e}")
            logger.info("🔄 Falling back to base model...")
            
            # Fallback to base model
            self.tokenizer = AutoTokenizer.from_pretrained(self.base_model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.base_model_name,
                torch_dtype=torch.float16,
                device_map="auto"
            )
            self.model_loaded = True
    
    def get_cache_key(self, prompt):
        """Generate cache key for prompt"""
        return hash(prompt.strip().lower())
    
    def cache_response(self, prompt, response):
        """Cache response with size limit"""
        cache_key = self.get_cache_key(prompt)
        
        # Limit cache size
        if len(self.response_cache) >= self.cache_size:
            # Remove oldest entry
            oldest_key = next(iter(self.response_cache))
            del self.response_cache[oldest_key]
        
        self.response_cache[cache_key] = response
    
    def get_cached_response(self, prompt):
        """Get cached response if available"""
        cache_key = self.get_cache_key(prompt)
        return self.response_cache.get(cache_key)
    
    def preprocess_prompt(self, prompt):
        """Optimize prompt for your trained model"""
        # Clean and format prompt
        prompt = prompt.strip()
        
        # Format for your insurance model
        if not prompt.endswith('?'):
            prompt += '?'
        
        return f"User: {prompt}\nAssistant:"
    
    def fast_generate(self, prompt):
        """Ultra-fast generation with all optimizations"""
        start_time = time.time()
        
        try:
            # Check cache first
            cached_response = self.get_cached_response(prompt)
            if cached_response:
                logger.info(f"⚡ Cache hit! Response in {time.time() - start_time:.3f}s")
                return cached_response
            
            # Ensure model is loaded
            if not self.model_loaded:
                self.load_model()
            
            # Preprocess prompt
            formatted_prompt = self.preprocess_prompt(prompt)
            
            # Tokenize with optimizations
            inputs = self.tokenizer(
                formatted_prompt,
                return_tensors="pt",
                truncation=True,
                max_length=self.max_input_length,
                padding=False
            )
            
            # Move to device
            if torch.cuda.is_available():
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Generate with maximum speed settings
            with torch.no_grad():
                with torch.cuda.amp.autocast() if torch.cuda.is_available() else torch.no_grad():
                    outputs = self.model.generate(
                        **inputs,
                        max_new_tokens=self.max_new_tokens,
                        do_sample=True,
                        temperature=self.temperature,
                        top_p=self.top_p,
                        top_k=self.top_k,
                        repetition_penalty=1.1,
                        pad_token_id=self.tokenizer.eos_token_id,
                        eos_token_id=self.tokenizer.eos_token_id,
                        use_cache=True,
                        num_beams=1,  # Greedy for speed
                        early_stopping=True,
                    )
            
            # Decode response
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract assistant response
            if "Assistant:" in response:
                response = response.split("Assistant:")[-1].strip()
            
            # Clean up response
            response = response.replace(formatted_prompt, "").strip()
            
            # Remove any remaining artifacts
            if response.startswith("User:"):
                response = response.split("Assistant:")[-1].strip()
            
            # Cache the response
            self.cache_response(prompt, response)
            
            generation_time = time.time() - start_time
            logger.info(f"⚡ Generated response in {generation_time:.2f}s")
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Generation error: {e}")
            return "Je suis désolé, une erreur s'est produite. Veuillez réessayer."

# Global client instance
_fast_client = None

def get_fast_client():
    """Get or create fast client instance"""
    global _fast_client
    if _fast_client is None:
        _fast_client = FastMistralClient()
    return _fast_client

def fast_chat_completion(prompt, max_tokens=100):
    """Fast chat completion function"""
    client = get_fast_client()
    
    # Override max tokens if specified
    if max_tokens != 100:
        client.max_new_tokens = max_tokens
    
    return client.fast_generate(prompt)

# Backward compatibility
def chat_completion(prompt, max_tokens=100):
    """Backward compatible chat completion"""
    return fast_chat_completion(prompt, max_tokens)

# Preload model on import (optional)
def preload_model():
    """Preload model for faster first response"""
    client = get_fast_client()
    client.load_model()

# Uncomment to preload model on import
# preload_model()
