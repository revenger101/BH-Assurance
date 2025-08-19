import torch

if torch.cuda.is_available():
    device = torch.device("cuda")
    print(f"Using GPU: {torch.cuda.get_device_name(0)}")
    # Test tensor operation on GPU
    x = torch.rand(1000, 1000, device=device)
    y = x @ x  # Matrix multiplication
    print("GPU test successful:", y.sum().item())
else:
    print("CUDA not available.")