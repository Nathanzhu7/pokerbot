import random
import pkrbot

FINAL_BOARD_CARDS = 6  # Toss/Hold'em ends with 6 community cards

FINAL_BOARD_CARDS = 6

# def convert_cards_to_int(cards):
#     if not cards:
#         return []
#     # If already ints, return as-is
#     if isinstance(cards[0], int):
#         return cards

#     rank_map = {'2': 0, '3': 1, '4': 2, '5': 3, '6': 4, '7': 5, '8': 6, '9': 7,
#                 'T': 8, 'J': 9, 'Q': 10, 'K': 11, 'A': 12}
#     suit_map = {'c': 0, 'd': 13, 'h': 26, 's': 39}

#     result = []
#     for c in cards:
#         rank_char = c[0].upper()
#         suit_char = c[1].lower()
#         result.append(suit_map[suit_char] + rank_map[rank_char])
#     return result

def card_to_int(card):
    """Convert Card object or string to integer 0-51"""
    if isinstance(card, int):
        return card
    card_str = str(card)  # Convert Card object to string like "Ah"
    rank_map = {'2': 0, '3': 1, '4': 2, '5': 3, '6': 4, '7': 5, '8': 6, '9': 7,
                'T': 8, 'J': 9, 'Q': 10, 'K': 11, 'A': 12}
    suit_map = {'c': 0, 'd': 13, 'h': 26, 's': 39}
    return suit_map[card_str[1].lower()] + rank_map[card_str[0].upper()]

def int_to_card(card_int):
    """Convert integer 0-51 to Card object"""
    ranks = '23456789TJQKA'
    suits = 'cdhs'
    rank_idx = card_int % 13
    suit_idx = card_int // 13
    return pkrbot.Card(ranks[rank_idx] + suits[suit_idx])

def str_to_card(card_input):
    """Convert string(s) (e.g., "Ah" or ["Ah", "Kd"]) to Card object(s)"""
    if not card_input:
        return []
    if isinstance(card_input, list):
        return [str_to_card(c) for c in card_input]
    if isinstance(card_input, str):
        return pkrbot.Card(card_input)
    # Already a Card object or something else, return as-is
    return card_input

def mc_equity(my_hole2, board, iters=500):
    # 1. Normalize inputs to ensure they are Card objects
    my_hole2 = str_to_card(my_hole2)
    board = str_to_card(board)

    # 2. Define the deck (integers 0-51) excluding known cards
    known_ints = {card_to_int(c) for c in my_hole2 + board}
    deck_ints = [c for c in range(52) if c not in known_ints]

    # 3. Initialize the win counter
    wins = 0.0

    # 4. Determine how many cards needed to fill the board to 6
    need_board = max(0, FINAL_BOARD_CARDS - len(board))

    # randomly sample the remaining cards for the board and the other players two hole cards

    for _ in range(iters):
        sample_ints = random.sample(deck_ints, need_board + 2)
        sample_cards = [int_to_card(i) for i in sample_ints]
        full_board = board + sample_cards[:need_board]
        opp_hole2 = sample_cards[need_board:]

        my_score = pkrbot.evaluate(my_hole2 + full_board)
        opp_score = pkrbot.evaluate(opp_hole2 + full_board)

        if my_score > opp_score:
            wins += 1.0
        elif my_score == opp_score:
            wins += 0.5

    return wins / iters

def best_discard_index(my_hole3, board, iters=10000):
    scores = []
    for i in range(3):
        discarded = my_hole3[i]
        remaining = my_hole3[:i] + my_hole3[i+1:] # The 2 cards you keep
        new_board = board + [discarded]     # The discard becomes public board

        # We simply maximize equity.
        # If the discard helps the opponent (random range), equity drops naturally.
        scores.append(mc_equity(remaining, new_board, iters=iters))

    # print("DEBUG scores:", scores, flush=True)
    # print("DEBUG card removed:", my_hole3[scores.index(max(scores))], 'with initial hole cards:', my_hole3, 'and board:', board, flush=True)
    # a higher mc_equity means the remaining cards in my hand are better
    return scores.index(max(scores))



# LAMBDA = 1.0  # tune this

# def discard_score(hand3, board, idx, iters=300):
#     """
#     hand3: list[int] length 3
#     board: list[int]
#     idx: index of card to discard (0,1,2)
#     """

#     discarded = hand3[idx]
#     remaining = [hand3[(idx+1)%3], hand3[(idx+2)%3]]
#     new_board = board + [discarded]

#     # Your Monte Carlo equity vs random opponent
#     strength = mc_equity(remaining, new_board, iters=iters)

#     # Board-only danger proxy (simple, fast)
#     # Use a fixed dummy hand so comparisons are consistent
#     dummy_hand = remaining
#     board_strength = mc_equity(dummy_hand, new_board, iters=iters//2)

#     return strength - LAMBDA * board_strength
