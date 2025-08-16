from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# Free Mistral model
MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.1"

# Load tokenizer and model
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, device_map="auto", torch_dtype=torch.float16)

def chat_completion(prompt, max_tokens=200):
    # Encode the prompt
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    
    # Generate response
    output = model.generate(
        **inputs,
        max_new_tokens=max_tokens,
        do_sample=True,
        temperature=0.7,
        top_p=0.9
    )
    
    # Decode the response
    response = tokenizer.decode(output[0], skip_special_tokens=True)
    
    return response
