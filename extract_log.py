#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 16 09:44:09 2020

@author: robert.tseng
"""

# =============================================================================
# import lib
# ============================================================================= 
import os
import re
import numpy as np
import json
from collections import defaultdict as ddict
import eval7
import random

# =============================================================================
# loading data 
# =============================================================================
# line_data = f.readline()
# while line_data:
#     room_id = re.findall('\[room (\d+)\]', line_data)
#     if room_id:
#         if room_id[0] not in room:
#             room[room_id[0]] = np.empty((1, 2), dtype = 'object')    
#     for sub_id in room:
#         if sub_id in line_data:
#             try:
#                 room[sub_id] = np.vstack((room[sub_id], np.asarray(line_data.split(' INFO  '))))
#             except:
#                 continue
#     line_data = f.readline()         
def data_split(room):
    # k = 0
    room_game = dict()
    for room_id in room:
        game = dict()
        k = 0
        for i in range(len(room[room_id])):
            line = room[room_id][i]
            # if 'start deal' in line:
            #     game[k] = [[], [], []]
            try:
                if not game:
                    k = 0
                if re.findall('\[deal\]banker:(.+)', line):
                    game[k] = [[], [], []]
                    data = re.findall('\[deal\]banker:(.+)', line)[0]
                    data = data.split(', allPlayers:')
                    game[k][0] = json.loads(data[1])
                if re.findall('\[ACTION\](.+)', line):
                    data = re.findall('\[ACTION\](.+)', line)[0]
                    data = data.split(' ')
                    data[0] = json.loads(data[0])
                    game[k][1].append(data)
                if re.findall('\[seeCard\]addCards:.+ baseCard:(.+)', line):
                    data = re.findall('\[seeCard\]addCards:.+ baseCard:(.+)', line)[0]
                    game[k][1].append(data)
                if 'end settle room' in line:
                    k += 1
            except:
                continue
        room_game[room_id] = game
    return room_game


def create_initial_state(players_number, first_number_of_players_hand, all_players_number=6):
    state = []
    funds = []
    for i in range(len(first_number_of_players_hand)):
        funds.append(first_number_of_players_hand[i][0]['totalGold'])
    fund_state = [i / max(funds) for i in funds] + [0] * (all_players_number - players_number)
    allin_state = [0] * all_players_number
    fold_state = [0] * players_number + [1] * (all_players_number - players_number)
    raise_state = [0] * all_players_number
    check_state = [0] * all_players_number
    card_state = [0] * 52
    win_rate_state = 0
    total_stakes = [0] * 6
    players_order_state = [0]
    # legal_action_state = [1] * 12

    state.extend(fund_state)
    state.extend(allin_state)
    state.extend(fold_state)
    state.extend(raise_state)
    state.extend(check_state)
    state.extend(card_state)
    state.append(win_rate_state)
    state.extend(total_stakes)
    state.extend(players_order_state)
    # state.extend(legal_action_state)

    return state


def get_action(round_hand):
    action_dict = {"check": 0, "fold": 1, "all-in": 2, "raise-1": 3, "raise-2": 4, "raise-3": 5, "raise-4": 6,
                   "raise-10": 7, "raise-20": 8,
                   "raise-50": 9, "raise-100": 10, "raise-200": 11}
    small_blind_bet = 2500
    action = [round_hand[1].replace('[', '').replace(']', ''), round_hand[2]]
    return_action = [0] * 12
    if action[1] == '0':
        if action[0] == 'fold':
            return_action[1] = 1
            # return action_dict['fold']
            return return_action
        if action[0] == 'pass':
            return_action[0] = 1
            # return action_dict['check']
            return return_action
    else:
        if action[0] == 'allin':
            return_action[2] = 1
            # return action_dict['all-in']
            return return_action
        money = int(action[1])
        ratio_bet = money / small_blind_bet
        if ratio_bet <= 1:
            return_action[3] = 1
            # return action_dict['raise-10']
            return return_action
        if ratio_bet <= 2:
            return_action[4] = 1
            # return action_dict['raise-20']
            return return_action
        if ratio_bet <= 3:
            return_action[5] = 1
            # return action_dict['raise-30']
            return return_action
        if ratio_bet <= 4:
            return_action[6] = 1
            # return action_dict['raise-40']
            return return_action
        if ratio_bet <= 10:
            return_action[7] = 1
            # return action_dict['raise-50']
            return return_action
        if ratio_bet <= 20:
            return_action[8] = 1
            # return action_dict['raise-60']
            return return_action
        if ratio_bet <= 50:
            return_action[9] = 1
            # return action_dict['raise-70']
            return return_action
        if ratio_bet <= 100:
            return_action[10] = 1
            # return action_dict['raise-80']
            return return_action
        if ratio_bet <= 200:
            return_action[11] = 1
            # return action_dict['raise-90']
            return return_action
        else:
            return_action[2] = 1
            # return action_dict['all-in']
            return return_action


# order start from 0
def calculate_players_order(first_number_of_players_hand):
    keys = []
    values = []
    for i in range(len(first_number_of_players_hand)):
        keys.append(first_number_of_players_hand[i][0]['chairId'])
        values.append(i)
    return dict(zip(keys, values))


def calculate_win_rate(cur_hand, community):
    compare_times = 1000
    card = ["♣2", "♣3", "♣4", "♣5", "♣6", "♣7", "♣8", "♣9", "♣10", "♣J", "♣Q", "♣K", "♣A",
            "♦2", "♦3", "♦4", "♦5", "♦6", "♦7", "♦8", "♦9", "♦10", "♦J", "♦Q", "♦K", "♦A",
            "♥2", "♥3", "♥4", "♥5", "♥6", "♥7", "♥8", "♥9", "♥10", "♥J", "♥Q", "♥K", "♥A",
            "♠2", "♠3", "♠4", "♠5", "♠6", "♠7", "♠8", "♠9", "♠10", "♠J", "♠Q", "♠K", "♠A"]
    card_convert = ["2c", "3c", "4c", "5c", "6c", "7c", "8c", "9c", "Tc", "Jc", "Qc", "Kc", "Ac",
                    "2d", "3d", "4d", "5d", "6d", "7d", "8d", "9d", "Td", "Jd", "Qd", "Kd", "Ad",
                    "2h", "3h", "4h", "5h", "6h", "7h", "8h", "9h", "Th", "Jh", "Qh", "Kh", "Ah",
                    "2s", "3s", "4s", "5s", "6s", "7s", "8s", "9s", "Ts", "Js", "Qs", "Ks", "As"]
    card_dict = dict(zip(card, card_convert))

    cur_hand_convert = []
    community_convert = []

    for i in cur_hand:
        cur_hand_convert.append(card_dict[i])

    if community:
        for j in community:
            community_convert.append(card_dict[j])

    win_count = 0
    for i in range(compare_times):
        sim_community = []
        if community_convert:
            for j in community_convert:
                sim_community.append(j)
        deck = list(set(card_convert)-set(cur_hand_convert)-set(sim_community))
        random.shuffle(deck)
        for j in range(5 - len(community_convert)):
            sim_community.append(deck.pop())

        hand = [eval7.Card(s) for s in cur_hand_convert + sim_community]
        # print("cur_hand: ", hand)
        hand_score = eval7.evaluate(hand)

        all_score = [hand_score]
        for j in range(5):
            opponent_card = []
            for k in range(2):
                opponent_card.append(deck.pop())
            opponent_hand = [eval7.Card(s) for s in opponent_card + sim_community]
            # print("opponent hand: ", opponent_hand)
            all_score.append(eval7.evaluate(opponent_hand))

        if hand_score == max(all_score):
            win_count += 1
    win_rate = win_count / compare_times
    return win_rate


def get_card_index(card_in_hand, card_state, community):
    card = ["♣2", "♣3", "♣4", "♣5", "♣6", "♣7", "♣8", "♣9", "♣T", "♣J", "♣Q", "♣K", "♣A",
            "♦2", "♦3", "♦4", "♦5", "♦6", "♦7", "♦8", "♦9", "♦T", "♦J", "♦Q", "♦K", "♦A",
            "♥2", "♥3", "♥4", "♥5", "♥6", "♥7", "♥8", "♥9", "♥T", "♥J", "♥Q", "♥K", "♥A",
            "♠2", "♠3", "♠4", "♠5", "♠6", "♠7", "♠8", "♠9", "♠T", "♠J", "♠Q", "♠K", "♠A"]
    index = list(range(0, 52))
    card_dict = dict(zip(card, index))
    for i in card_in_hand:
        if '10' in i:
            card_state[card_dict[i.replace('10', 'T')]] = 1
        else:
            card_state[card_dict[i]] = 1
    if community:
        for i in community:
            if '10' in i:
                card_state[card_dict[i.replace('10', 'T')]] = 1
            else:
                card_state[card_dict[i]] = 1
    return card_state


def update_state(state, round_hand, check_card, order_dict, pre_action, first_number_of_players_hand):
    fund_state = state[0:6]
    allin_state = state[6:12]
    fold_state = state[12:18]
    raise_state = state[18:24]
    check_state = state[24:30]
    card_state = [0] * 52
    win_rate_state = state[82:83]
    total_stakes = state[83:89]
    players_order_state = state[89:90]
    # legal_action_state = [1] * 12

    if not pre_action:
        card_state = get_card_index(round_hand[0]['cards'].split("|"), card_state, [])
        win_rate_state = calculate_win_rate(round_hand[0]['cards'].split("|"), [])
    else:
        right_now_order = order_dict[round_hand[0]['chairId']]
        if right_now_order - 1 < 0:
            pre_order = len(order_dict) - 1
        else:
            pre_order = right_now_order - 1

        funds = []
        for i in range(len(first_number_of_players_hand)):
            funds.append(first_number_of_players_hand[i][0]['totalGold'])
        total_stakes[pre_order] = int(pre_action[1]) / max(funds)
        fund_state[pre_order] -= total_stakes[pre_order]
        if pre_action[0] == 'fold':
            fold_state[pre_order] = 1
        if pre_action[0] == 'pass':
            check_state[pre_order] = 1
        if pre_action[0] == 'raise':
            raise_state[pre_order] = 1
        if pre_action[0] == 'allin':
            allin_state[pre_order] = 1
        players_order_state[0] = right_now_order
        if not check_card:
            card_state = get_card_index(round_hand[0]['cards'].split("|"), card_state, [])
            win_rate_state = calculate_win_rate(round_hand[0]['cards'].split("|"), [])
        else:
            card_state = get_card_index(round_hand[0]['cards'].split("|"), card_state, check_card.split("|"))
            win_rate_state = (calculate_win_rate(round_hand[0]['cards'].split("|"), check_card.split("|")))**(6 - sum(fold_state)-1)
    state = []
    state.extend(fund_state)
    state.extend(allin_state)
    state.extend(fold_state)
    state.extend(raise_state)
    state.extend(check_state)
    state.extend(card_state)
    state.append(win_rate_state)
    state.extend(total_stakes)
    state.extend(players_order_state)
    # state.extend(legal_action_state)

    return state


if __name__ == '__main__':
    filepath = './log_tmp'
    all_file_list = os.listdir(filepath)
    room = ddict(list)
    for filename in all_file_list:
        f = open(filepath + '/' + filename, 'r')
        while True:
            line = f.readline()
            if line:
                room_id = re.findall('\[room (\d+)\]|\[observerId:(\d+)\]', line)
                if room_id:
                    room_id = ''.join(room_id[0])
                    time = line.split('INFO ')[0]
                    context = line.split(room_id)[1].replace('\n', '')
                    if 'leave' not in context and 'enter' not in context and 'kick' not in context:
                        room[room_id].append(f'{time} - {context}')
            else:
                break
        # context isn't ordered by time.
        for room_id, context in room.items():
            room[room_id] = sorted(context)
        room_game = data_split(room)

    ####

    # i: room_id
    # key: game_num
    # k: round_hand
    room_id_list = list(room_game.keys())
    input_list = []
    output_list = []
    for i in room_id_list:
        # print(i)
        for j in range(len(room_game[i])):
            try:
                players_number = len(room_game[i][j][0])
                state = create_initial_state(players_number, room_game[i][j][1][:players_number])
                pre_action = []
                check_card = []
                try:
                    for k in range(len(room_game[i][j][1])):
                        if players_number == 6 & len(room_game[i][j][1][:players_number]) > 5:
                            # print(room_game[i][j][1][k])  # 在第i的roomid下 第j場遊戲 第k手
                            order_dict = calculate_players_order(room_game[i][j][1][:players_number])
                            if isinstance(room_game[i][j][1][k], str):
                                check_card = room_game[i][j][1][k]
                            else:
                                next_state = update_state(state, room_game[i][j][1][k], check_card, order_dict, pre_action, room_game[i][j][1][:players_number])
                                pre_action = [room_game[i][j][1][k][1].replace('[', '').replace(']', ''), room_game[i][j][1][k][2]]
                                action = get_action(room_game[i][j][1][k])
                                state = next_state
                                input_list.append(state)
                                output_list.append(action)
                except:
                    continue
            except:
                continue

    np.savetxt('input_list_all', input_list)
    np.savetxt('output_list_all', output_list)