# scripts/infer_peft.py
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import PeftModel

BASE = "mistralai/Mistral-7B-Instruct-v0.1"
ADAPTER_DIR = "mistral-lora/outputs/mistral-7b-instruct-lora"

tokenizer = AutoTokenizer.from_pretrained(BASE, use_fast=True)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                         bnb_4bit_use_double_quant=True, bnb_4bit_compute_dtype=torch.bfloat16)

base = AutoModelForCausalLM.from_pretrained(BASE, device_map="auto", quantization_config=bnb)
model = PeftModel.from_pretrained(base, ADAPTER_DIR)
model.eval()

def chat_completion(prompt, max_new_tokens=200):
    # Use your dataset delimiter so model sees what it was trained on
    text = prompt + "\n\n###\n\n"
    inputs = tokenizer(text, return_tensors="pt").to(model.device)
    with torch.no_grad():
        out = model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=True, temperature=0.7, top_p=0.9)
    return tokenizer.decode(out[0], skip_special_tokens=True)

print(chat_completion("Qu’est-ce qu’une franchise ?"))
