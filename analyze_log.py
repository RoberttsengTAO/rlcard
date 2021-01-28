#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 16 09:44:09 2020

@author: robert.tseng

2020/05/18 Chen Yu Shi
"""

# todo: 整理賭注

import json
import os
import re
from collections import defaultdict as ddict
from collections import deque

room = ddict(int)
get_count = ddict(lambda: [0] * 6)
fold_count = ddict(lambda: [0] * 6)
bet_data = deque()


def get_room_history(log_name):
    log_path = os.path.abspath(os.path.dirname(__file__)) + f'/{log_name}'
    f = open(log_path, 'r', encoding='utf-8')

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
    return room


def handle_table():
    start, player_size = 0, 0
    for room_id, context in room.items():
        for event in context:
            if 'banker' in event:
                player_data = json.loads(event.split('allPlayers:')[1])
                player_size = len(list(player_data.keys()))
                start = 0
            elif '[ACTION]' in event and start < player_size:
                data = json.loads(re.findall("(\{.*\})", event)[0])
                action = re.findall("\[.*\].*\[(.*)\]", event)[0]
                card = handle_card(data['cards'])
                get_count[card][start] += 1
                if action == 'fold':
                    fold_count[card][start] += 1
                start += 1
    return get_count, fold_count


def stat_bet():
    for room_id, context in room.items():
        for event in context:
            if '[ACTION]' in event:
                room_info = json.loads(re.findall("(\{.*\})", event)[0])
                action, cost = re.findall("\[.*\].*\[(.*)\](.*)", event)[0]
                if action == 'raise':
                    total_gold = room_info['totalGold']
                    bet_data.append(float(cost))
    return bet_data


# some tool
def handle_card(card):
    card = card.replace('10', 'T')
    same_suit = card[0] == card[3]
    ans = ('s' if same_suit else 'o') + ''.join(sorted([card[1], card[4]]))
    return ans


def fold_rate(target):
    f = fold_count[target]
    g = get_count[target]
    return [f[i] / g[i] for i in range(6)]


if __name__ == '__main__':
    log_list = os.listdir('log')

    for i in log_list:
        rooms = get_room_history('log/' + i)
        handle_table()

    total_fold_rate = dict()
    for card in get_count.keys():
        total_fold_rate[card] = [fold_count[card][i] / get_count[card][i] for i in range(6)]
    sorted(total_fold_rate.items(), key=lambda x: x[1])
    # pprint.pprint(room)
    # room_game = data_split(room)
