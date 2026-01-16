import torch
import torch.optim as optim
from .model import PokerPolicy
from .encoder import encode_state

class RLAgent:
    def __init__(self, training_mode=False, model_path="smart_brain.pth"):
        self.training_mode = training_mode
        self.model_path = model_path

        # Initialize Brain
        self.policy = PokerPolicy(input_size=113, output_size=4)
        try:
            self.policy.load_state_dict(torch.load(model_path))
        except:
            pass # Start fresh if no file found

        if self.training_mode:
            self.optimizer = optim.Adam(self.policy.parameters(), lr=0.001)
            self.policy.train()
        else:
            self.policy.eval()

        # Memory
        self.saved_log_probs = []

    def select_action(self, my_cards, board, stacks, pips, street, legal_actions):
        """
        Handles encoding, masking, and action selection.
        Returns: (Action Object, log_prob)
        """
        # 1. Encode
        state_vec = encode_state(my_cards, board, stacks, pips, street)

        # 2. Forward Pass
        probs = self.policy(state_vec)

        # 3. Mask & Sample (Logic from previous helper)
        action_idx, log_prob = self._sample_masked_action(probs, legal_actions)

        if self.training_mode:
            self.saved_log_probs.append(log_prob)

        return action_idx  # Return the index (0-3)

    def update_policy(self, reward):
        """Called at end of round to learn."""
        if not self.training_mode or len(self.saved_log_probs) == 0:
            return

        policy_loss = []
        discounted_reward = reward
        GAMMA = 0.99

        # Backwards credit assignment
        for log_prob in reversed(self.saved_log_probs):
            policy_loss.append(-log_prob * discounted_reward)
            discounted_reward *= GAMMA

        self.optimizer.zero_grad()
        loss = torch.stack(policy_loss).sum()
        loss.backward()
        self.optimizer.step()

        self.saved_log_probs = [] # Reset

    def save(self):
        torch.save(self.policy.state_dict(), self.model_path)

    def _sample_masked_action(self, probs, legal_actions):
        # ... (Insert the masking logic we discussed earlier here) ...
        # Return action_index, log_prob
        pass
