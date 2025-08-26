"""
Speed Configuration for BH Assurance Chat

This file contains all speed optimization settings that can be easily adjusted
to balance between response quality and speed.
"""

# Model Configuration
MODEL_CONFIG = {
    # Base model settings
    "base_model": "mistralai/Mistral-7B-Instruct-v0.1",
    "trained_model_path": "bhagent/outputs/sft_mistral_combined/checkpoint-882",
    
    # Device settings
    "device": "auto",  # "auto", "cuda", "cpu"
    "torch_dtype": "float16",  # "float16", "float32"
    "low_cpu_mem_usage": True,
    
    # Memory optimization
    "offload_folder": "bhagent/outputs/offload",
    "use_cache": True,
}

# Generation Settings (Speed vs Quality Trade-offs)
GENERATION_CONFIG = {
    # Speed Settings (Lower = Faster)
    "max_input_length": 256,    # Reduce for faster processing
    "max_new_tokens": 100,      # Reduce for faster generation
    
    # Quality Settings
    "temperature": 0.7,         # Lower = more deterministic
    "top_p": 0.9,              # Nucleus sampling
    "top_k": 40,               # Top-k sampling
    "repetition_penalty": 1.1,  # Prevent repetition
    
    # Speed Optimizations
    "do_sample": True,          # Enable sampling
    "num_beams": 1,            # Use greedy search (faster)
    "early_stopping": True,     # Stop early when possible
    "use_cache": True,         # Enable KV cache
}

# Cache Settings
CACHE_CONFIG = {
    "enable_response_cache": True,
    "cache_size": 100,          # Number of responses to cache
    "cache_ttl": 3600,         # Cache time-to-live in seconds
    "enable_tokenization_cache": True,
}

# Performance Presets
PERFORMANCE_PRESETS = {
    "ultra_fast": {
        "max_input_length": 128,
        "max_new_tokens": 50,
        "temperature": 0.5,
        "top_k": 20,
        "cache_size": 200,
    },
    
    "fast": {
        "max_input_length": 256,
        "max_new_tokens": 100,
        "temperature": 0.7,
        "top_k": 40,
        "cache_size": 100,
    },
    
    "balanced": {
        "max_input_length": 512,
        "max_new_tokens": 150,
        "temperature": 0.7,
        "top_k": 50,
        "cache_size": 50,
    },
    
    "quality": {
        "max_input_length": 1024,
        "max_new_tokens": 200,
        "temperature": 0.8,
        "top_k": 60,
        "cache_size": 25,
    }
}

# Current active preset
ACTIVE_PRESET = "fast"  # Change this to switch presets

# Logging Configuration
LOGGING_CONFIG = {
    "log_response_times": True,
    "log_cache_hits": True,
    "log_model_loading": True,
    "detailed_logging": False,  # Set to True for debugging
}

# Advanced Optimizations
ADVANCED_CONFIG = {
    "enable_torch_compile": True,    # Requires PyTorch 2.0+
    "enable_mixed_precision": True,  # Use automatic mixed precision
    "enable_gradient_checkpointing": False,  # Usually not needed for inference
    "enable_flash_attention": False,  # Requires specific hardware
}

def get_config(preset=None):
    """Get configuration with optional preset override"""
    if preset is None:
        preset = ACTIVE_PRESET
    
    config = {
        "model": MODEL_CONFIG.copy(),
        "generation": GENERATION_CONFIG.copy(),
        "cache": CACHE_CONFIG.copy(),
        "logging": LOGGING_CONFIG.copy(),
        "advanced": ADVANCED_CONFIG.copy(),
    }
    
    # Apply preset overrides
    if preset in PERFORMANCE_PRESETS:
        preset_config = PERFORMANCE_PRESETS[preset]
        config["generation"].update(preset_config)
    
    return config

def get_speed_recommendations():
    """Get speed optimization recommendations"""
    return {
        "immediate_improvements": [
            "Reduce max_new_tokens to 50-100 for faster responses",
            "Use temperature 0.5-0.7 for more deterministic output",
            "Enable response caching for repeated questions",
            "Use top_k sampling (20-40) instead of top_p only"
        ],
        
        "hardware_improvements": [
            "Use GPU (CUDA) instead of CPU",
            "Increase GPU memory for larger batch sizes",
            "Use NVMe SSD for faster model loading",
            "Enable mixed precision (float16) training"
        ],
        
        "advanced_optimizations": [
            "Implement model quantization (8-bit or 4-bit)",
            "Use TensorRT for NVIDIA GPUs",
            "Implement response streaming for perceived speed",
            "Use model distillation for smaller, faster models"
        ]
    }

def print_current_config():
    """Print current configuration"""
    config = get_config()
    
    print("🔧 Current Speed Configuration")
    print("=" * 40)
    print(f"Active Preset: {ACTIVE_PRESET}")
    print(f"Max Input Length: {config['generation']['max_input_length']}")
    print(f"Max New Tokens: {config['generation']['max_new_tokens']}")
    print(f"Temperature: {config['generation']['temperature']}")
    print(f"Top-K: {config['generation']['top_k']}")
    print(f"Cache Size: {config['cache']['cache_size']}")
    print(f"Response Cache: {'Enabled' if config['cache']['enable_response_cache'] else 'Disabled'}")

if __name__ == "__main__":
    print_current_config()
    
    print("\n💡 Speed Recommendations:")
    recommendations = get_speed_recommendations()
    
    print("\n🚀 Immediate Improvements:")
    for rec in recommendations["immediate_improvements"]:
        print(f"  • {rec}")
    
    print("\n🖥️ Hardware Improvements:")
    for rec in recommendations["hardware_improvements"]:
        print(f"  • {rec}")
    
    print("\n⚡ Advanced Optimizations:")
    for rec in recommendations["advanced_optimizations"]:
        print(f"  • {rec}")
