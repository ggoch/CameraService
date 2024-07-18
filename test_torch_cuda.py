import torch

# 检查PyTorch是否可用
print("PyTorch version:", torch.__version__)

# 检查CUDA是否可用
cuda_available = torch.cuda.is_available()
print("CUDA available:", cuda_available)

if cuda_available:
    print("CUDA version:", torch.version.cuda)
    print("Number of GPUs available:", torch.cuda.device_count())
    print("GPU name:", torch.cuda.get_device_name(0))
else:
    print("CUDA is not available.")