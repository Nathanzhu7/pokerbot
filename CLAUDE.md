# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MIT Pokerbots 2026 engine and bot development environment. This year's variant: players receive 3 hole cards pre-flop and must discard one face-up after the flop (Toss/Hold'em).

## Running the Game Engine

```bash
# Run a game between two bots
.venv/bin/python engine.py
```

Configure matchups in `config.py`:
- `PLAYER_1_PATH` / `PLAYER_2_PATH`: Bot directories (e.g., `./python_skeleton`, `./simple_bot`)
- `NUM_ROUNDS`: Number of hands per game (default 6000)
- `ENFORCE_GAME_CLOCK`: Toggle time enforcement

## Bot Development

### Python Bot Structure (python_skeleton/)

Each bot needs:
- `player.py`: Entry point implementing the `Bot` class
- `commands.json`: Build/run commands (`{"build": [], "run": ["python3", "player.py"]}`)
- `skeleton/`: Framework files (actions, states, runner)

Key methods to implement in `Player(Bot)`:
- `handle_new_round(game_state, round_state, active)`: Called at round start
- `handle_round_over(game_state, terminal_state, active)`: Called at round end
- `get_action(game_state, round_state, active)`: Return action (FoldAction, CallAction, CheckAction, RaiseAction, DiscardAction)

### Game Flow & Street Values

Streets progress: `0` (preflop) → `2` (discard 1) → `3` (discard 2) → `4` (turn) → `5` (river) → `6` (showdown)

Discard phase: After flop, player B (out of position) discards first (street 2), then player A (street 3). Discarded cards become visible board cards.

### Actions

```python
from skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction, DiscardAction

# DiscardAction takes card index (0, 1, or 2)
DiscardAction(card=1)  # Discard middle card

# RaiseAction takes total amount
min_raise, max_raise = round_state.raise_bounds()
RaiseAction(amount=min_raise)
```

### Hand Evaluation

Use `pkrbot` library for hand evaluation:
```python
import pkrbot
score = pkrbot.evaluate(hand_cards + board_cards)  # Higher score = better hand
```

## Current Bot Implementations

### python_skeleton (RL_Learner)
Reinforcement learning bot:
- `brain/model.py`: Neural network policy (114 inputs → 6 action outputs)
- `brain/encoder.py`: State encoding (cards as one-hot vectors + normalized chip counts)
- `brain/agent.py`: RL agent with REINFORCE algorithm
- `fixed_actions/preflop.py`: Hardcoded preflop strategy
- `fixed_actions/discard.py`: Monte Carlo discard selection

Action mapping: 0=Fold, 1=Check/Call, 2=Min raise, 3=Small raise, 4=Medium raise, 5=All-in

### simple_bot
Monte Carlo equity-based bot:
- `utils.py`: MC equity calculations, card conversions
- `helpers.py`: Strength calculation and betting decisions
- Uses pot odds vs hand equity for decisions

## Other Language Skeletons

- `java_skeleton/`: Java bot template (requires Java 8+)
- `cpp_skeleton/`: C++ bot template (requires C++17, CMake 3.8+, Boost)

Build C++ bot:
```bash
cd cpp_skeleton && mkdir build && cd build
cmake .. && make
```

## Output Files

- `gamelog.txt`: Complete game history
- `{PLAYER_NAME}.txt`: Bot stdout/stderr logs
- `rl_live.log`: RL training metrics (python_skeleton)
- `*.pth`: PyTorch model checkpoints
