import os
import json
from collections import OrderedDict
import numpy as np
import rlcard
from keras.utils.np_utils import to_categorical
from rlcard.games.holdem.card import holdemCard as Card

# Read required docs
ROOT_PATH = rlcard.__path__[0]

# a map of abstract action to its index and a list of abstract action
with open(os.path.join(ROOT_PATH, 'games/holdem/jsondata/action_space.json'), 'r') as file:
    ACTION_SPACE = json.load(file, object_pairs_hook=OrderedDict)
    ACTION_LIST = list(ACTION_SPACE.keys())
suit_dict = {2:0, 4:1, 8:2, 16:3}

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
    #final_list.extend(encode(state['player'], state['player_size']))
    final_list.extend(state['players_fund'])
    final_list.extend([i * 1 for i in state['all_in']])
    final_list.extend([i * 1 for i in state['players_fold']])
    final_list.extend(state['players_raise_count'])
    final_list.extend(state['players_check_count'])
    # final_list.extend(state['community_suit'])
    # final_list.extend(state['community_rank'])
    # final_list.extend(encode_hand(state['hand'], state['check']))
    dummy_card = encode_card(state['hand_suit']+state['community_suit'],\
                             state['hand_rank'] + state['community_rank'])
    final_list.extend(dummy_card)
    # final_list.extend(state['hand_rank'])
    # final_list.extend(state['hand_suit'])
    final_list.append(state['win_rate'][state['round']-1])
    final_list.extend(state['total_stakes'])
    final_list.append(state['player'])
    return np.array(final_list)

def encode_card(card_suit, card_rank):
    dummy_card = [0]*52
    for i in range(len(card_suit)):
        sub_suit = card_suit[i]
        sub_rank = card_rank[i]
        dummy_card[suit_dict[sub_suit]*13+ sub_rank - 2] = 1
    return dummy_card 


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
