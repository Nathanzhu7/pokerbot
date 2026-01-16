from utils import mc_equity, best_discard_index

def test_mc_equity(hole, board):
    print(mc_equity(hole, board))

def test_best_discard_index(my_hole_3, board_2):
    print(best_discard_index(my_hole_3, board_2))


print("Test 2: Hidden Trips, expected index 2 ('Tc')")
test_best_discard_index(['6c', '6d', 'Tc'], ['6s', '2h'])

# 3. The "Hidden Straight Draw"
# Situation: You have T, J. Board has Q, K. You need a 9 or A for a straight.
# Choice: Discard 2h.
# Why: You want to keep the connectors (T, J) to maximize your chances of hitting the straight. The 2h is trash.
# Expected: Index 2 ('2h')
print("Test 3: Hidden Straight Draw, expected index 2 ('2h')")
test_best_discard_index(['Ts', 'Js', '2h'], ['Qd', 'Kd'])


# 4. The "Flush Draw Disguise"
# Situation: You have Ah, 5h. Board has 2h, 9h. You are 1 heart away from the Nut Flush.
# Choice: Discard Ks.
# Why: Discarding the Ks keeps 2 hearts in your hand (hidden). If you discard the 5h, the board will have 3 hearts, making it obvious a flush is possible and giving the opponent equity if they hold a heart.
# Expected: Index 2 ('Ks')
print("Test 4: Flush Draw Disguise, expected index 2 ('Ks')")
test_best_discard_index(['Ah', '5h', 'Ks'], ['2h', '9h'])


# 5. The "High Card Power"
# Situation: You have Ace, King. Board is low trash.
# Choice: Discard 2c.
# Why: In a heads-up game, high cards (Ace/King) have massive showdown value. You never discard your power cards for a low kicker.
# Expected: Index 2 ('2c')
print("Test 5: High Card Power, expected index 2 ('2c')")
test_best_discard_index(['As', 'Kd', '2c'], ['5h', '9s'])
