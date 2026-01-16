import random
from skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction
from utils import mc_equity

# -------------------------------------------------------------------------
# STRENGTH CALCULATOR
# -------------------------------------------------------------------------
def calculate_strength(my_cards, board_cards, time_left):
    """
    Determines hand strength using Monte Carlo.
    Handles the special 3-card pre-discard case.
    """
    # Case A: Pre-discard (3 cards) - Approximation
    if len(my_cards) == 3:
        possibilities = []
        for i in range(3):
            # Simulate keeping pair (i, j) and discarding k
            kept_cards = my_cards[:i] + my_cards[i+1:]
            # We simulate lightly (50 iters) for speed
            possibilities.append(mc_equity(kept_cards, board_cards, iters=50))
        return max(possibilities)

    # Case B: Standard Play (2 cards)
    # Dynamic iterations: Think deeper if we have time
    iters = 500 if time_left > 15 else 100
    return mc_equity(my_cards, board_cards, iters=iters)


# -------------------------------------------------------------------------
# BETTING BRAIN
# -------------------------------------------------------------------------
def get_betting_action(strength, pot_odds, pot_total, continue_cost, legal_actions, round_state):
    """
    Decides whether to Check, Call, Raise, or Fold based on strength.
    """
    # SCENARIO A: We are facing a bet (Defense)
    if continue_cost > 0:
        return _respond_to_bet(strength, pot_odds, pot_total, legal_actions, round_state)

    # SCENARIO B: We are first to act (Offense)
    else:
        return _open_betting(strength, pot_total, legal_actions, round_state)


def _respond_to_bet(strength, pot_odds, pot_total, legal_actions, round_state):
    # 1. MONSTER: Raise for value (Trap or Bomb)
    if strength >= 0.90 and RaiseAction in legal_actions:
        # If pot is tiny, overbet (1.5x) to build it. If huge, just 1.0x.
        factor = 1.5 if pot_total < 50 else 1.0
        return _get_raise_action(round_state, pot_total, factor)

    # 2. STRONG: Raise sometimes, Call otherwise
    if strength >= 0.75 and strength >= pot_odds:
        if RaiseAction in legal_actions and random.random() < 0.50:
            return _get_raise_action(round_state, pot_total, 0.75) # Standard Raise
        return CallAction()

    # 3. MARGINAL: Call if odds are good
    if strength >= pot_odds:
        return CallAction()

    # 4. WEAK: Fold
    return FoldAction()


def _open_betting(strength, pot_total, legal_actions, round_state):
    # 1. MONSTER: Overbet to build pot
    if strength > 0.90 and RaiseAction in legal_actions:
        return _get_raise_action(round_state, pot_total, 1.5) # 150% Pot

    # 2. STRONG: Value bet
    if strength > 0.65 and RaiseAction in legal_actions:
        # Mix it up: sometimes check to trap (20%), usually bet (80%)
        if random.random() < 0.80:
            return _get_raise_action(round_state, pot_total, 0.6) # 60% Pot

    # 3. WEAK/MARGINAL: Check
    return CheckAction()


def _get_raise_action(round_state, pot_total, multiplier):
    """
    Safely calculates a legal raise amount based on a pot multiplier.
    """
    min_raise, max_raise = round_state.raise_bounds()

    target_amt = int(min_raise + (pot_total * multiplier))

    # Clamp to legal bounds
    clean_amt = min(max_raise, max(min_raise, target_amt))
    return RaiseAction(clean_amt)
