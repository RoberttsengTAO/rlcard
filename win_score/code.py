#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 22 09:26:01 2020

@author: robert.tseng
"""

# =============================================================================
# lib
# =============================================================================
import matplotlib.pyplot as plt
import numpy as np 
import json
import os
import re
from collections import defaultdict as ddict
import os 
import json
# =============================================================================
#  functions 
# =============================================================================
def log_extract(log_path):
    game = []
    f = open(log_path, 'r', encoding='utf-8')
    while True:
        line = f.readline()
        if line:
            player = re.findall('texas player', line)
            if player:
                # print(line)
                time = line.split(' INFO ')[0]
                room_id = re.findall('\[bot room (\d+)\]', line)[0]
                money = line.split(' = ')[1].replace('\n', '')
                # room[room_id] = money
                game.append(f'{time} {money}')
        else:
            break
    return sorted(game)

def log_extract_fage(log_path):
    game = []
    f = open(log_path, 'r', encoding='utf-8') 
    while True:
        line = f.readline()
        if line:
            player = re.findall('texas player', line)
            if player:
                time = line.split(' INFO ')[0]
                room_id = re.findall('\[bot room (\d+)\]', line)[0]
                money = re.findall('delta = (\d+|-\d+)', line)[0]
                fage = re.findall('fage = (.+)', line)[0]
                # room[room_id] = money
                game.append(f'{time} {money} {fage} {room_id}')
        else:
            break
    return sorted(game)

def get_room_history(log_path):
    # log_path = os.path.abspath(os.path.dirname(__file__)) + f'/{log_name}'
    f = open(log_path, 'r', encoding='utf-8')

    while True:
        line = f.readline()
        if line:
            room_id = re.findall('\[room (\d+)\]|\[observerId:(\d+)\]|\[bot room (\d+)\]', line)
            if room_id:
                player = re.findall('texas player', line)
                room_id = ''.join(room_id[0])
                time = line.split('INFO ')[0]
                context = line.split(room_id+']')[1].replace('\n', '')
                if 'leave' not in context and 'enter' not in context and 'kick' not in context:
                    room[room_id].append(f'{time} - {context}')
                if player:
                    print(room_id)             
        else:
            break
    # context isn't ordered by time.
    for room_id, context in room.items():
        room[room_id] = sorted(context)
    return room
def texas_extract(game_room):
    lose_c = []
    for room_id, sub_room in game_room.items():
        # tm1, tm2, mon, fage, room_id, fage_bet = i.split() 
        # sub_room = game_room[room_id]
        start_game = False
        # print(room_id)
        for  sub_context in sub_room:
            if re.findall("let's deal", sub_context):
                bet = re.findall('fage_bet = (\d+)', sub_context)[0]
                start_game = True
                human_id = None
                game_list = [None]*16
                game_list[14] = int(bet) // 100
                game_list[15] = room_id
            if start_game:
                if re.findall('banker:{', sub_context):
                    info = json.loads(sub_context.split(', ')[1][11:])
                    for i,j in info.items():
                        game_list[int(i)-1] = j['cards']
                if re.findall('human (\d+) setMove', sub_context):
                    human_id, chair = re.findall('human (\d+) setMove --> chair = (\d+)', sub_context)[0]
                    game_list[7] = chair
                    game_list[8] = human_id
                    game_list[9] = game_list[int(chair)-1]
                if re.findall('addCards', sub_context):
                    open_card = re.findall('baseCard:(.+)', sub_context)[0]
                    game_list[6] = open_card
                if re.findall('round (\d+) ', sub_context):
                    user_id, coin, tax = re.findall('user (\d+) .+ delta=(\d+|-\d+).+gameTax:(\d+)', sub_context)[0]
                    print(human_id, user_id)
                    if human_id == user_id:
                        game_list[11] = int(coin) // 100
                        game_list[12] = int(tax) // 100
                # if re.findall('')
                if re.findall('texas player', sub_context):
                    game_list[10] = int(re.findall('delta = (\d+|-\d+)', sub_context)[0]) // 100
                    game_list[13] = re.findall('fage = (.+)', sub_context)[0]
                    start_game = False
                    lose_c.append(game_list)
    return lose_c
game = []
game_fage = ddict(str)
# room_rpc = sorted(room_rpc)
def log_extract_rpc_fage(log_path):
    game = []
    f = open(log_path, 'r', encoding = 'utf-8')
    while True:
        line = f.readline()
        if line:
            fage = re.findall('\[Java\] setmove fage', line)
            create = re.findall('setMove success', line)
            if fage:
                time = line.split('INFO ')[0][:-2]
                fage = line.split('[Java] setmove fage: ')[1].replace('\n', '')
                game.append(f'{time} {fage}')
            if create:
                time = line.split('INFO ')[0][:-2]
                room_id = re.findall("\[BotRoom (\d+)\]", line)[0]
                game.append(f'{time} {room_id}')
        else:
            break
    game = sorted(game)
    for i in range(0, len(game), 2):
        sub_time = ' '.join(game[i].split(' ')[:2])
        room_id = game[i].split(' ')[2]
        fage = game[i+1].split(' ')[2]
        if fage == 'true' or fage == 'false':
            game_fage[room_id] = fage
            game_time[room_id] = sub_time
            
    
def draw_time_series(score, time, log_path):
    score_cumsum = np.cumsum(score)
    bins = [-20000, -15000, -10000, -5000, -2000, \
            0, 2000, 5000, 10000, 15000, 20000]
    with plt.rc_context({'axes.edgecolor':'white', 'xtick.color':'black',\
                         'ytick.color':'white', 'figure.facecolor':'white'}):
        f = plt.figure(figsize=(19, 10), facecolor = 'black')
        ## time series plot 
        ax1 = f.add_subplot(211, facecolor = 'black')
        ax1.set_title(log_path, color = 'w')
        plt.subplots_adjust(hspace = .4)
        ax1.set_ylabel('Unit game money', color = 'w')
        ax1.set_xlabel('Time', color = 'w')
        ax1.plot(score)
        ax1.plot([0, len(score)], [0, 0], linestyle='dashed',color = 'r')
        ax1.set_xticks(range(0, len(time), 200))
        ax1.set_xticklabels(time[::200], color = 'w', rotation = -90)
        ax1.set_yticks(bins)
        ax1.set_yticklabels(bins, color = 'w')
        # cusmsum plot 
        ax2 = f.add_subplot(212, facecolor = 'black')
        ax2.plot(score_cumsum)
        ax2.set_ylim([-2*10**5, 2*10**5])
        ax2.plot([0, len(score)], [0, 0], linestyle='dashed',color = 'r')
        ax2.set_ylabel('Cumsum money', color = 'w')
def split_tuple(fage_false_tuple, log_path):
    score = [ i  for i, _ in fage_false_tuple]
    time = [j for _, j in fage_false_tuple]
    draw_time_series(score, time, log_path)
    
def plot_hist(score, log_path):
    np_score = np.asarray(score)
    np_score = np_score[np_score != 0]
    h = max(np.histogram(np_score)[0])
    # bins = sorted(np.append(np.histogram(np_score)[1], 0))
    bins = [-10000, -5000, -2000, -1000, -500, -300,\
            0, 300, 500, 1000, 2000, 5000, 10000]
    with plt.rc_context({'axes.edgecolor':'white', 'xtick.color':'white',\
                         'ytick.color':'white', 'figure.facecolor':'white'}):
        f = plt.figure(figsize=(10, 10), facecolor = 'black')
        ax1 = f.add_subplot(111, facecolor = 'black')
        plt.hist(np_score, bins = bins)
        ax1.plot([0, 0], [0, h], color = 'r', linestyle = 'dashed')
        ax1.set_title(log_path, color = 'w')
        ax1.set_xlabel('Unit game money', color = 'w')
        ax1.set_ylabel('Count', color = 'w')
        ax1.set_xticks(bins)
        ax1.set_xticklabels(bins, color = 'w', rotation = 90)

def fage_split(game):
    fage_dict = ddict(list)
    fage_list = ['close', 'passive', 'initiative']
    for i in game:
        for fage in fage_list:
            if fage in i:
                fage_dict[fage].append(i)
    return fage_dict
        
# =============================================================================
# 
# =============================================================================
if __name__ == '__main__':
    ## plot 
    os.chdir('/Users/robert.tseng/Documents/fix_version/holdem_game/win_score')
    log_list = os.listdir('./zh')
    fun = lambda x: re.search('game.log', x)
    game_log_list =  list(filter(fun, log_list))
    log_path = './zh/'+ game_log_list[0]
    game = log_extract_fage(log_path)
    # game = log_extract(log_path)
    game[0].split()
    score = list(map(lambda x: int(x.split()[2]) // 100, game))
    time = list(map(lambda x: x.split()[1], game))
    draw_time_series(score, time, log_path)
    plot_hist(score, log_path)
    p = sum(filter(lambda x: x > 0, score))*0.95
    p1 = sum(filter(lambda x: x > 0, score))*0.05
    p2 = sum(filter(lambda x: x < 0, score))
    (p1 + p) / len(list(filter(lambda x: x > 0, score)))
    p2 -p1 + p
    ## anay
    room = ddict(list)
    game_room =get_room_history(log_path)
    cont1 = []
    value = []
    for room_id, cont in game_room.items():
        for line in cont:
            player = re.findall('texas player', line)
            fage_bet = re.findall('fage_bet', line)
            if fage_bet:
                bet = line.split(' = ')[1]
            if player:
                time = line.split(' - ]')[0]
                money = re.findall('delta = (\d+|-\d+)', line)[0]
                fage = re.findall('fage = (.+)', line)[0]
                # room[room_id] = money
                if int(money) >= 250000:
                    cont1.append(f'{time} {money} {fage} {room_id} {bet}')
                    value.append([int(bet)//100, int(money)// 100])
    lose_c = []
    for room_id, sub_room in game_room.items():
        # tm1, tm2, mon, fage, room_id, fage_bet = i.split() 
        # sub_room = game_room[room_id]
        start_game = False
        # print(room_id)
        for  sub_context in sub_room:
            if re.findall("let's deal", sub_context):
                bet = re.findall('fage_bet = (\d+)', sub_context)[0]
                start_game = True
                human_id = None
                game_list = [None]*16
                game_list[14] = int(bet) // 100
                game_list[15] = room_id
            if start_game:
                if re.findall('banker:{', sub_context):
                    info = json.loads(sub_context.split(', ')[1][11:])
                    for i,j in info.items():
                        game_list[int(i)-1] = j['cards']
                if re.findall('human (\d+) setMove', sub_context):
                    human_id, chair = re.findall('human (\d+) setMove --> chair = (\d+)', sub_context)[0]
                    game_list[7] = chair
                    game_list[8] = human_id
                    game_list[9] = game_list[int(chair)-1]
                if re.findall('addCards', sub_context):
                    open_card = re.findall('baseCard:(.+)', sub_context)[0]
                    game_list[6] = open_card
                if re.findall('round (\d+) ', sub_context):
                    user_id, coin, tax = re.findall('user (\d+) .+ delta=(\d+|-\d+).+gameTax:(\d+)', sub_context)[0]
                    print(human_id, user_id)
                    if human_id == user_id:
                        game_list[11] = int(coin) // 100
                        game_list[12] = int(tax) // 100
                # if re.findall('')
                if re.findall('texas player', sub_context):
                    game_list[10] = int(re.findall('delta = (\d+|-\d+)', sub_context)[0]) // 100
                    game_list[13] = re.findall('fage = (.+)', sub_context)[0]
                    start_game = False
                    lose_c.append(game_list)
                    # print(game_list)
    lose_c = sorted(lose_c, key = lambda x: x[10])
    p = np.asarray(lose_c)
    p = p[ p[:, 8] != None, :] 
    p = p[np.argsort(p[:, 8]), :]
    count = Counter(p[:, 8])
    result_sum = ddict(int)
    for i in range(len(p)):
        sub_p = p[i, ]
        result_sum[sub_p[8]] += sub_p[10]
    id_p =  p[ p[:, 10] == 0 , :]
    id_p = id_p[id_p[: , 11] != None, :]
    np.sum(id_p[:, 11])
    count['164192878']
    plt.plot(id_p[:, 10])
sub_room = game_room['2480568']
f = open('ex_489580.log', 'w')
for i in sub_room:
    print(i)
    f.write(i+"\n")

f.close()
