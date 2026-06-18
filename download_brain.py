from transformers import pipeline
import torch

print("Connecting to Hugging Face to fetch a micro language model...")

# 1. We download a super tiny text generator model (gpt2) 
# and tell it to use your M5 chip (device="mps")
generator = pipeline('text-generation', model='gpt2', device='mps')

print("\nBrain loaded successfully into your M5 graphics cores!")

# 2. Let's test its baseline intelligence with a legal-style prompt
prompt = "In a standard commercial lease agreement, the tenant is responsible for"
print(f"\nFeeding prompt to AI: '{prompt}'\n")

# 3. Run the generation
result = generator(prompt, max_length=40, num_return_sequences=1)

print("--- AI RESPONSE ---")
print(result[0]['generated_text'])
print("-------------------")