import torch
import torch.nn as nn
import torch.nn.functional as F

class PokerPolicy(nn.Module):
    def __init__(self, input_size, output_size):
        super(PokerPolicy, self).__init__()
        # Layer 1: Input -> 128 neurons
        self.fc1 = nn.Linear(input_size, 128)

        # Layer 2: 128 -> 128 neurons
        self.fc2 = nn.Linear(128, 128)

        # Layer 3: 128 -> Actions (Output probabilities)
        self.fc3 = nn.Linear(128, output_size)

    def forward(self, x):
        # Activation Function: ReLU (Rectified Linear Unit)
        # It allows the network to learn complex, non-linear patterns
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))

        # Output Function: Softmax
        # Converts raw numbers into probabilities that sum to 1.0
        # dim=-1 ensures it calculates across the action list
        x = F.softmax(self.fc3(x), dim=-1)
        return x
