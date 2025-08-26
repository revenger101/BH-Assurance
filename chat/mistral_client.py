from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import torch
import time
import logging
from functools import lru_cache

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Model configuration
BASE_MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.1"
TRAINED_MODEL_PATH = "bhagent/outputs/sft_mistral_combined/checkpoint-882"

# Global variables for model caching
_tokenizer = None
_model = None
_model_loaded = False

def load_model():
    """Load model with memory-efficient configuration"""
    global _tokenizer, _model, _model_loaded

    if _model_loaded:
        return _tokenizer, _model

    logger.info("Loading model with memory optimization...")
    start_time = time.time()

    try:
        # Load tokenizer
        _tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_NAME)
        if _tokenizer.pad_token is None:
            _tokenizer.pad_token = _tokenizer.eos_token

        # Try to load with trained adapters first
        try:
            logger.info("Attempting to load trained model...")
            # Load base model with conservative memory settings
            _model = AutoModelForCausalLM.from_pretrained(
                BASE_MODEL_NAME,
                torch_dtype=torch.float16,
                device_map="auto",
                low_cpu_mem_usage=True,
                offload_folder="outputs/offload",
                max_memory={0: "6GiB", "cpu": "8GiB"}  # Conservative memory limits
            )

            # Load trained adapters
            _model = PeftModel.from_pretrained(_model, TRAINED_MODEL_PATH)
            logger.info("✅ Trained model loaded successfully!")

        except Exception as trained_error:
            logger.warning(f"Could not load trained model: {trained_error}")
            logger.info("🔄 Falling back to base model...")

            # Fallback to base model only
            _model = AutoModelForCausalLM.from_pretrained(
                BASE_MODEL_NAME,
                torch_dtype=torch.float16,
                device_map="auto",
                low_cpu_mem_usage=True,
                max_memory={0: "6GiB", "cpu": "8GiB"}
            )
            logger.info("✅ Base model loaded successfully!")

        _model.eval()  # Set to evaluation mode
        _model_loaded = True

        load_time = time.time() - start_time
        logger.info(f"Model loaded in {load_time:.2f} seconds")

        return _tokenizer, _model

    except Exception as e:
        logger.error(f"❌ Critical error loading model: {e}")
        logger.info("🔄 Trying minimal configuration...")

        # Last resort: minimal configuration
        try:
            _tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_NAME)
            _model = AutoModelForCausalLM.from_pretrained(
                BASE_MODEL_NAME,
                torch_dtype=torch.float16,
                device_map="cpu"  # Force CPU if GPU fails
            )
            _model_loaded = True
            logger.info("✅ Model loaded on CPU")
            return _tokenizer, _model
        except Exception as final_error:
            logger.error(f"❌ Failed to load model: {final_error}")
            raise final_error

@lru_cache(maxsize=100)
def get_cached_tokenization(prompt_hash):
    """Cache tokenization for repeated prompts"""
    return None  # Placeholder for caching logic

def chat_completion(prompt, max_tokens=100, temperature=0.7):
    """Optimized chat completion with speed improvements"""
    start_time = time.time()

    try:
        # Load model if not already loaded
        tokenizer, model = load_model()

        # Simple prompt format - no complex formatting for speed
        formatted_prompt = prompt

        # Tokenize with speed optimizations
        inputs = tokenizer(
            formatted_prompt,
            return_tensors="pt",
            truncation=True,
            max_length=256,  # Reduced for speed
            padding=False
        )

        # Move to device
        if torch.cuda.is_available():
            inputs = {k: v.to(model.device) for k, v in inputs.items()}

        # Generate with maximum speed settings
        with torch.no_grad():  # Disable gradient computation
            output = model.generate(
                **inputs,
                max_new_tokens=max_tokens,  # Reduced default
                do_sample=True,
                temperature=temperature,
                top_p=0.9,
                top_k=40,  # Reduced for speed
                repetition_penalty=1.1,
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id,
                use_cache=True,  # Enable KV cache
                num_beams=1,  # Greedy search for speed
                early_stopping=True,  # Stop early when possible
            )

        # Decode response efficiently
        response = tokenizer.decode(output[0], skip_special_tokens=True)

        # Simple cleanup - remove input prompt
        if formatted_prompt in response:
            response = response.replace(formatted_prompt, "").strip()

        generation_time = time.time() - start_time
        logger.info(f"Response generated in {generation_time:.2f} seconds")

        return response

    except Exception as e:
        logger.error(f"Error in chat completion: {e}")
        return f"Je suis désolé, une erreur s'est produite. Veuillez réessayer."
