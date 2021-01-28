import os
import json
from collections import OrderedDict
import numpy as np
import rlcard

from rlcard.games.zhj.card import ZhjCard as Card

# Read required docs
ROOT_PATH = rlcard.__path__[0]

# a map of abstract action to its index and a list of abstract action
with open(os.path.join(ROOT_PATH, 'games/zhj/jsondata/action_space.json'), 'r') as file:
    ACTION_SPACE = json.load(file, object_pairs_hook=OrderedDict)
    ACTION_LIST = list(ACTION_SPACE.keys())


def init_deck():
    """
    Generate poke deck of 52 cards
    """
    deck = []
    card_info = Card.info
    for suit in card_info['suit']:
        for number in card_info['number']:
            deck.append(Card(suit, number))

    return deck


def encode_state(state):
    """
    # game info
        state['players_fund'] = [i.fund for i in self.players]
        state['players_fold'] = [i.fold for i in self.players]
        state['players_check'] = [i.check for i in self.players]
        state['cur_bet_level'] = self.round.current_bet_level
        state['total_stakes'] = self.round.total_stakes
        state['player_size'] = self.num_players
        state['all_in_num'] = self.round.all_in_num
        # player info
        state['player'] = player_id
        state['init fund'] = player.init_fund
        state['fund'] = player.fund
        state['fold'] = player.fold
        state['check'] = player.check
        # after check, know
        state['hand'] = [i.str for i in player.hand]
        state['power'] = player.power
    """
    final_list = []
    final_list.extend(encode(state['player'], state['player_size']))
    final_list.append(state['fund'])
    final_list.append(state['fold'] * 1)
    final_list.append(state['check'] * 1)
    # final_list.extend(encode_hand(state['hand'], state['check']))
    final_list.append(state['power'] if state['check'] else 110706/10**6)

    # final_list.extend(state['players_fund'])
    if state['all_in_num']:
        final_list.append(state['all_in_money'])
    else:
        final_list.append(min(state['players_fund']))
    final_list.extend([i * 1 for i in state['players_fold']])
    final_list.extend([i * 1 for i in state['players_check']])
    final_list.append(state['cur_bet_level'])
    final_list.append(state['total_stakes'])
    # final_list.append(state['player_size'])
    final_list.append(state['all_in_num'])

    return np.array(final_list)


def encode_hand(hand, check_status):
    ans = []
    # is_suit status: 0 same suit, 1 no suit, unknown
    # card: 13 type + 1(unknown) = 14
    if check_status:
        suits = [i.suit for i in hand]
        is_suit = [1, 0, 0] if len(set(suits)) == 1 else [0, 1, 0]
        for i in hand:
            ans += encode(i.rank, 14)
    else:
        is_suit = [0, 0, 1]
        for _ in range(3):
            ans += encode(13, 14)
    ans += is_suit
    return ans


def encode(target, size):
    ans = [0] * size
    ans[target] = 1
    return ans


if __name__ == '__main__':
    # hand = [Card('H', 'A'), Card('S', 'A'), Card('D', 'A')]
    # print(encode_hand(hand, True))

    # compute state size
    from rlcard.games.zhj.game import ZhjGame

    game = ZhjGame()
    game.init_game()

    state = game.get_state(0)
    print(state)
    result = encode_state(state)
    print(result)
    print(len(result))
