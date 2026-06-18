import torch

# 1. We create a fake "sentence" using random numbers (How AI sees words)
dummy_text_data = torch.rand(1, 5)

# 2. We tell PyTorch to send this data straight to your M5 Apple Silicon chip
m5_processor = torch.device("mps")
processed_data = dummy_text_data.to(m5_processor)

# 3. We print out the result to prove the engine works
print("Engine is LIVE on M5 Chip!")
print("Here is what the raw data looks like:")
print(processed_data)