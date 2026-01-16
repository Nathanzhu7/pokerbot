'''
Simple example pokerbot, written in Python.
'''
from skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction, DiscardAction
from skeleton.states import GameState, TerminalState, RoundState
from skeleton.states import NUM_ROUNDS, STARTING_STACK, BIG_BLIND, SMALL_BLIND
from skeleton.bot import Bot
from skeleton.runner import parse_args, run_bot

import random

# from poker import Deck, Card
# from poker.hand import Combo
import pkrbot

from utils import best_discard_index, mc_equity
from helpers import calculate_strength, get_betting_action

class Player(Bot):
    '''
    A pokerbot.
    '''

    def __init__(self):
        '''
        Called when a new game starts. Called exactly once.

        Arguments:
        Nothing.

        Returns:
        Nothing.
        '''
        pass

    def handle_new_round(self, game_state, round_state, active):
        '''
        Called when a new round starts. Called NUM_ROUNDS times.

        Arguments:
        game_state: the GameState object.
        round_state: the RoundState object.
        active: your player's index.

        Returns:
        Nothing.
        '''
        my_bankroll = game_state.bankroll  # the total number of chips you've gained or lost from the beginning of the game to the start of this round
        # the total number of seconds your bot has left to play this game
        game_clock = game_state.game_clock
        round_num = game_state.round_num  # the round number from 1 to NUM_ROUNDS
        my_cards = round_state.hands[active]  # your cards
        big_blind = bool(active)  # True if you are the big blind
        pass

    def handle_round_over(self, game_state, terminal_state, active):
        '''
        Called when a round ends. Called NUM_ROUNDS times.

        Arguments:
        game_state: the GameState object.
        terminal_state: the TerminalState object.
        active: your player's index.

        Returns:
        Nothing.
        '''
        my_delta = terminal_state.deltas[active]  # your bankroll change from this round
        previous_state = terminal_state.previous_state  # RoundState before payoffs
        street = previous_state.street  # 0,2,3,4,5,6 representing when this round ended
        my_cards = previous_state.hands[active]  # your cards
        # opponent's cards or [] if not revealed
        opp_cards = previous_state.hands[1-active]
        pass

    def get_action(self, game_state, round_state, active):
        '''
        Where the magic happens - your code should implement this function.
        Called any time the engine needs an action from your bot.

        Arguments:
        game_state: the GameState object.
        round_state: the RoundState object.
        active: your player's index.

        Returns:
        Your action.
        '''
        legal_actions = round_state.legal_actions()  # the actions you are allowed to take
        # 0, 3, 4, or 5 representing pre-flop, flop, turn, or river respectively
        street = round_state.street
        my_cards = round_state.hands[active]  # your cards
        board_cards = round_state.board  # the board cards
        # the number of chips you have contributed to the pot this round of betting
        my_pip = round_state.pips[active]
        # the number of chips your opponent has contributed to the pot this round of betting
        opp_pip = round_state.pips[1-active]
        # the number of chips you have remaining
        my_stack = round_state.stacks[active]
        # the number of chips your opponent has remaining
        opp_stack = round_state.stacks[1-active]
        continue_cost = opp_pip - my_pip  # the number of chips needed to stay in the pot
        # the number of chips you have contributed to the pot
        my_contribution = STARTING_STACK - my_stack
        # the number of chips your opponent has contributed to the pot
        opp_contribution = STARTING_STACK - opp_stack

        # Only use DiscardAction if it's in legal_actions (which already checks street)
        # legal_actions() returns DiscardAction only when street is 2 or 3

        # ---------------------------------------------------------------------
        # 1. DISCARD LOGIC
        # ---------------------------------------------------------------------

        if DiscardAction in legal_actions:
            best_discard_idx = best_discard_index(my_cards, board_cards)
            return DiscardAction(best_discard_idx)

        # 2. METRICS
        strength = calculate_strength(my_cards, board_cards, game_state.game_clock)
        pot_total = (STARTING_STACK - my_stack) + (STARTING_STACK - opp_stack)

        if continue_cost > 0:
            pot_odds = continue_cost / (pot_total + continue_cost)
        else:
            pot_odds = 0

        # 3. DECISION (Delegate to helpers.py)
        return get_betting_action(
            strength, pot_odds, pot_total, continue_cost, legal_actions, round_state
        )

        from model import PokerPolicy
    # import torch

    # class Player(Bot):
    #     def __init__(self):
    #         # Load the trained brain
    #         self.brain = PokerPolicy(input_size=106, output_size=4)
    #         self.brain.load_state_dict(torch.load("smart_brain.pth"))
    #         self.brain.eval() # Switch to "Test Mode" (No learning)

    #     def get_action(self, ...):
    #         # 1. See
    #         state_vector = encode_state(...)

    #         # 2. Think
    #         probs = self.brain(state_vector)

    #         # 3. Act (Pick the action with highest probability)
    #         action_idx = torch.argmax(probs).item()
    #         return self._index_to_action(action_idx)


if __name__ == '__main__':
    run_bot(Player(), parse_args())
