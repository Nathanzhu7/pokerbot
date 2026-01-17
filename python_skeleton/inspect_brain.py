import torch
import os

# 1. Define the path
model_path = "smart_brain.pth"

# 2. Check if it exists
if not os.path.exists(model_path):
    print(f"Error: Could not find {model_path}")
    print("Make sure you are running this from the 'python_skeleton' folder!")
    exit()

# 3. Load the dictionary
print(f"--- Loading {model_path} ---")
try:
    state_dict = torch.load(model_path)
except Exception as e:
    print(f"Failed to load: {e}")
    exit()

# 4. Print stats for every layer
print(f"{'LAYER NAME':<20} | {'SHAPE':<20} | {'MEAN':<10} | {'STD':<10}")
print("-" * 70)

for key, value in state_dict.items():
    # 'key' is the layer name (e.g., fc1.weight)
    # 'value' is the tensor of numbers

    # Calculate simple stats
    mean_val = value.float().mean().item()
    std_val = value.float().std().item()
    shape_str = str(list(value.shape))

    print(f"{key:<20} | {shape_str:<20} | {mean_val:<10.5f} | {std_val:<10.5f}")

print("-" * 70)
print("Inspection Complete.")
