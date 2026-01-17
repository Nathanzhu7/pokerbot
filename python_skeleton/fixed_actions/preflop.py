from skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction

def get_preflop_action(round_state, active):
        '''
        Basic Pre-Flop Strategy:
        1. Raise with Pairs (22+) and Double High Cards (AK, QJ).
        2. Call with any Single High Card (A2, K9) or Connectors.
        3. Check/Fold everything else.
        '''
        legal_actions = round_state.legal_actions()
        my_cards = round_state.hands[active]

        # --- 1. Card Parsing ---
        # Cards are strings like 'As', 'Td', '2c'.
        # Rank is index 0. Suit is index 1.
        rank1 = my_cards[0][0]
        rank2 = my_cards[1][0]
        suit1 = my_cards[0][1]
        suit2 = my_cards[1][1]

        # Helper: Convert rank char to approximate strength integer
        # 2=2, ... 9=9, T=10, J=11, Q=12, K=13, A=14
        ranks = '23456789TJQKA'
        val1 = ranks.index(rank1) + 2
        val2 = ranks.index(rank2) + 2

        is_pair = (val1 == val2)
        is_suited = (suit1 == suit2)
        is_high_card = (val1 >= 10 or val2 >= 10) # 10, J, Q, K, A
        is_connector = (abs(val1 - val2) == 1) # e.g., 9T, 67

        # --- 2. Action Logic ---

        # A. PREMIUM: Pairs or Two High Cards (e.g., AA, 99, AK, QJ)
        # Strategy: RAISE (Build the pot)
        if is_pair or (val1 >= 10 and val2 >= 10):
            if RaiseAction in legal_actions:
                min_raise, max_raise = round_state.raise_bounds()
                # Standard open: min_raise usually works well
                return RaiseAction(min_raise)
            elif CallAction in legal_actions:
                return CallAction()

        # B. PLAYABLE: Suited Connectors, Single High Card, or Any Suited
        # Strategy: CALL (See a cheap flop)
        if is_high_card or is_connector or is_suited:
            if CallAction in legal_actions:
                return CallAction()
            if CheckAction in legal_actions:
                return CheckAction()

        # C. JUNK: Low unsuited unconnected cards (e.g., 72o, 94o)
        # Strategy: CHECK (Free) or FOLD
        if CheckAction in legal_actions:
            return CheckAction()

        return FoldAction()
