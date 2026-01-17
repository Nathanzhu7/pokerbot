import torch

def encode_state(my_cards, board_cards, my_stack, opp_stack, my_pip, opp_pip, street):
    """
    Encodes the poker game state into a single tensor for the neural network.

    Inputs:
        my_cards: list of card strings (e.g., ['As', 'Th'])
        board_cards: list of card strings
        my_stack, opp_stack: int (chips remaining)
        my_pip, opp_pip: int (chips in pot this round)
        street: int (0=Preflop, 3=Flop, 4=Turn, 5=River)

    Returns:
        torch.Tensor of shape (113,)
    """

    # 1. ENCODE CARDS (One-Hot)
    # 52 inputs for my cards, 52 inputs for board
    my_hand_vec = _cards_to_vec(my_cards)
    board_vec = _cards_to_vec(board_cards)

    # 2. ENCODE STREET (One-Hot)
    street_map = {
        0: 0,  # Pre-Flop
        4: 1,  # Flop Betting
        5: 2,  # Turn Betting
        6: 3   # River Betting
    }

    street_vec = [0, 0, 0, 0]
    if street in street_map:
        street_vec[street_map[street]] = 1
    if street in street_map:
        street_vec[street_map[street]] = 1

    # 3. ENCODE CHIPS (Normalized Floats)
    # We normalize stacks by 400 (Starting Stack)
    # We normalize pot/bets by 800 (Total Chips in Play)

    my_stack_val = my_stack / 400.0
    opp_stack_val = opp_stack / 400.0

    pot_total = (400 - my_stack) + (400 - opp_stack)
    pot_val = pot_total / 800.0

    # Pips (current round bets) help the bot know if it's facing a raise
    my_pip_val = my_pip / 400.0
    opp_pip_val = opp_pip / 400.0

    # Cost to call is a critical feature
    cost_val = (opp_pip - my_pip) / 400.0

    # Combine all features into one list
    # Sizes: 52 + 52 + 4 + 6 = 114 inputs
    features = my_hand_vec + board_vec + street_vec + \
               [my_stack_val, opp_stack_val, pot_val, my_pip_val, opp_pip_val, cost_val]

    return torch.tensor(features, dtype=torch.float32)

def _cards_to_vec(cards):
    """Helper to convert list of card strings to 52-bit binary vector."""
    vec = [0] * 52
    for card in cards:
        idx = _card_str_to_int(card)
        if 0 <= idx < 52:
            vec[idx] = 1
    return vec

def _card_str_to_int(card_str):
    """
    Converts a card string (e.g., 'Ah', 'Td') to an integer 0-51.
    Ranks: 2=0, 3=1, ..., A=12
    Suits: s=0, h=1, d=2, c=3
    Formula: rank * 4 + suit
    """
    rank_char = card_str[0]
    suit_char = card_str[1]

    ranks = '23456789TJQKA'
    suits = 'shdc' # standard suit order for bots usually

    rank = ranks.index(rank_char)
    suit = suits.index(suit_char)

    return rank * 4 + suit
