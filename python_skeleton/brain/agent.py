import torch
import torch.optim as optim
from .model import PokerPolicy
from .encoder import encode_state
from skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction
import os

class RLAgent:
    def __init__(self, training_mode=False, model_path="smart_brain.pth"):
        self.training_mode = training_mode

        # --- PATH FIX START ---
        # 1. Get the path to this file (brain/agent.py)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 2. Go up one level to python_skeleton/
        bot_dir = os.path.dirname(current_dir)
        # 3. Force the full path for the brain file
        self.model_path = os.path.join(bot_dir, model_path)
        # --- PATH FIX END ---

        # Initialize Brain
        self.policy = PokerPolicy(input_size=114, output_size=4)
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

    def select_action(self, my_cards, board, stacks, pips, street, legal_actions, active=None):
        """
        Handles encoding, masking, and action selection.
        """
        # --- 1. Fix: Unpack Lists to Integers ---
        # player.py sends stacks=[my_stack, opp_stack]
        my_stack = stacks[0]
        opp_stack = stacks[1]
        my_pip = pips[0]
        opp_pip = pips[1]

        # --- 2. Encode ---
        # Note: If you added the 'active' argument to encoder.py for position,
        # make sure to pass it here. If not, remove 'active' from this call.
        state_vec = encode_state(
            my_cards,
            board,
            my_stack,
            opp_stack,
            my_pip,
            opp_pip,
            street,
            # active  <-- Uncomment this line ONLY if you updated encode_state to accept 'active'
        )

        # --- 3. Forward Pass ---
        probs = self.policy(state_vec)

        # --- 4. Mask & Sample ---
        action_idx, log_prob = self._sample_masked_action(probs, legal_actions)

        if self.training_mode:
            self.saved_log_probs.append(log_prob)

        return action_idx

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
        """
        1. Masks out illegal moves (sets prob to 0).
        2. Re-normalizes remaining probabilities.
        3. Samples an action.
        """
        # --- 1. Create the Mask ---
        # Map: 0=Fold, 1=Check/Call, 2=RaiseMin, 3=RaiseMax
        mask = [0.0, 0.0, 0.0, 0.0]

        # Check specific classes in legal_actions set
        if FoldAction in legal_actions:
            mask[0] = 1.0

        if CheckAction in legal_actions or CallAction in legal_actions:
            mask[1] = 1.0

        if RaiseAction in legal_actions:
            mask[2] = 1.0 # Allow Small Raise
            mask[3] = 1.0 # Allow Big Raise

        mask = torch.tensor(mask)

        # --- 2. Apply Mask & Renormalize ---
        masked_probs = probs * mask

        # Safety: If sum is 0 (shouldn't happen if logic is correct),
        # fallback to uniform probability over legal moves
        if masked_probs.sum() == 0:
            masked_probs = mask

        # Divide by total to make sure they sum to 1.0 again
        masked_probs /= masked_probs.sum()

        # --- 3. Sample ---
        if self.training_mode:
            # Exploration: Roll the dice based on probabilities
            dist = torch.distributions.Categorical(masked_probs)
            action_idx = dist.sample()
            log_prob = dist.log_prob(action_idx)
            return action_idx.item(), log_prob
        else:
            # Competition: Always pick the highest probability (Greedy)
            action_idx = torch.argmax(masked_probs)
            return action_idx.item(), 0.0 # No log_prob needed in eval

    def index_to_action(self, action_idx, legal_actions, min_raise, max_raise):
        """
        Translates the Neural Net's output index (0-3) into an Engine Action object.
        """
        # 0: Fold
        if action_idx == 0:
            # CRITICAL FIX: Never fold if checking is free!
            if CheckAction in legal_actions:
                return CheckAction()
            return FoldAction()

        # 1: Check / Call
        if action_idx == 1:
            if CheckAction in legal_actions:
                return CheckAction()
            return CallAction()

        # 2: Raise Min
        if action_idx == 2:
            if RaiseAction in legal_actions:
                safe_amount = int(min_raise + 0.33 * (max_raise - min_raise))
                return RaiseAction(safe_amount)
            # Fallback
            return CheckAction() if CheckAction in legal_actions else CallAction()

        # 3: Raise Max
        if action_idx == 3:
            if RaiseAction in legal_actions:
                return RaiseAction(max_raise)
            # Fallback
            return CheckAction() if CheckAction in legal_actions else CallAction()

        return CheckAction()
