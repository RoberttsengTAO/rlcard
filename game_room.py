#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 14 09:32:38 2020

@author: robert.tseng
"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  6 11:11:10 2020

@author: robert.tseng
"""
# =============================================================================
# import lib
# =============================================================================
import os
#os.chdir('/Users/robert.tseng/Documents/fix_version/holdem_game')
from copy import deepcopy
import rlcard
from rlcard.envs.holdem import holdemEnv
from rlcard.games.holdem.dealer import holdemDealer
from rlcard.games.holdem.player import holdemPlayer
from rlcard.games.holdem.round import holdemRound
from rlcard.games.holdem.game import holdemGame
from rlcard.games.holdem.card import computer_power
from rlcard.agents.random_agent_2 import RandomAgent as Alex
from rlcard.agents.random_agent_1 import RandomAgent as Yushi
from rlcard.agents.ac_agent import A2Cagent
import sys
import re
import time
import json
from collections import OrderedDict
import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd 
# =============================================================================
# plot function 
# =============================================================================
def plt_win_fund_rate(funds, win_rate, players):
    f = plt.figure(figsize=(10,3), facecolor = 'black')
    ax1 = f.add_subplot(121, facecolor = 'black')
    ax2 = f.add_subplot(122, facecolor = 'black')
    max1 = max(map(abs, funds))
    ## First plot
    ax1.set_xlim([- (max1+100), max1+100])
    ax1.set_ylim([-0.5, len(players)-0.5])
    for i, row in enumerate(funds): 
        if row < 0:
            color = 'g'
        else:
            color = 'r'
        ax1.barh(i*1, row, \
                color= color, align='center',
                edgecolor='w')
        ax1.plot([- (max1+100), max1+100], [i, i],color = 'w', \
                 linestyle='dashed')
    ax1.plot([0,0], [-0.5, len(players)+0.5],color = 'w')
    ax1.set_yticks(range(0, len(players)))
    ax1.set_yticklabels(players, color = 'w')
    ax1.spines['top'].set_visible(False)
    # ax1.spines['bottom'].set_color('w')
    ax1.spines['right'].set_color('w')
    ax1.spines['left'].set_visible(False)
    ax1.set_xlabel('Funds', color = 'w')
    ax1.set_ylabel('Players', color = 'w')
    ax1.set_title('Win Funds plot', color = 'w')
    ax1.tick_params(axis='x', color = 'w')
    [t.set_color('w') for t in ax1.xaxis.get_ticklabels()]
    ax1.xaxis.label.set_color('w')
    ## Second plot
    ax2.tick_params(axis='x', color = 'w')
    ax2.tick_params(axis='y', color = 'w')
    ax2.set_facecolor('black')       
    ax2.set_ylim([0, 1])
    ax2.set_xlabel('Game Round', color = 'w')
    ax2.set_ylabel('Win rate', color = 'w')
    ax2.plot(win_rate)
    ax2.legend(players,loc=(1.04,0))
    ax2.set_title('Win Rate plot', color = 'w')
    ax2.spines['left'].set_color('w')
    ax2.spines['right'].set_color('w')
    ax2.spines['bottom'].set_color('w')
    ax2.spines['top'].set_color('w')
    [t.set_color('w') for t in ax2.yaxis.get_ticklabels()]
    [t.set_color('w') for t in ax2.xaxis.get_ticklabels()]
    plt.show()

def win_count_compute(win_count, players):
    if len(players) ==1:
        win_count[:, players[0].player_id] += 1
    else:
        for player in players:
            win_count[:, player.player_id] += 1
    return win_count
    
# =============================================================================
# Game setting 
# =============================================================================
eval_env = holdemEnv()
state_size = eval_env.state_shape[0]
action_size = eval_env.action_num
sess = tf.Session()
### setting Players 
players = ['Yushi', 'Alex','Yushi','Alex', 'Yushi','Robert']
agents = [Yushi(action_size),Alex(action_size),Yushi(action_size)
         ,Alex(action_size)
         ,Yushi(action_size),A2Cagent(sess, state_size, action_size, layers=[48, 48])]
# agents[0].actor.load_weights('/Users/robert.tseng/Documents/acagentreward_model_0.h5')
agents[5].actor.load_weights('/Users/robert.tseng/Documents/model.h5')
# agents[5].actor.load_weights('/Users/robert.tseng/Documents/rl_all_138.h5')
eval_env.set_agents(agents)
ROOT_PATH = rlcard.__path__[0]
with open(os.path.join(ROOT_PATH, 'games/holdem/jsondata/action_space.json'), 'r') as file:
    ACTION_SPACE = json.load(file, object_pairs_hook=OrderedDict)
    ACTION_LIST = list(ACTION_SPACE.keys())
com = computer_power()
open_num = [0, 0, 3, 4, 5]
# =============================================================================
#  Starting 
# =============================================================================
diff_funds = np.zeros((len(players)))
fund = np.zeros((1,len(players)))
win_count = np.zeros((1,len(players)))
win_rate = np.zeros((1,len(players)))
if __name__ == '__main__':
    num_players= eval_env.player_num
    # small_bet = int(sys.argv[2])
    # try:
    for i in range(1, 1001):
        # try:
        game_count = 0
        state, player_id = eval_env.init_game()
        set_human = np.random.choice(range(num_players))
        comm_list = [i.suit_str + i.number_str for i in eval_env.game.community]
        community = ' '.join(comm_list)
        print('Game starting time:'+ time.ctime()+'\n')
        print('Setting game community card: {}\n'.format(community))
        player_id = 0
        for player in eval_env.game.players:
            hand = ' '.join([j.suit_str + j.number_str for j in player.hand])
            power = com.eval_hand(player.hand, eval_env.game.community)
            print('Player {} hand card: {} and power: {} win_rate: {} \n'.format(str(player_id), hand, str(power), player.win_rate))
            player_id += 1
        while not eval_env.game.round.is_over:
            if eval_env.game.round.count != game_count:
                print('='*50 + 'Round:{}'.format(eval_env.game.round.count) + '='*50+'\n')
                print('='*30 + 'Open card:{}\n'.format(comm_list[:open_num[eval_env.game.round.count]]))
                game_count = eval_env.game.round.count 
            # if eval_env.game.round.current_player != set_human:
            action = eval_env.agents[eval_env.game.round.current_player].eval_step(state)
            # if eval_env.game.round.current_player == 1:
            print('{} {}\n'.format(eval_env.game.round.total_stakes, 
              eval_env.game.round.current_player))
            print(ACTION_LIST[action])
            print('{} execute {}\n'.format(str(eval_env.game.round.current_player), ACTION_LIST[action]))
            next_state, next_player_id = eval_env.step(action)
            state = next_state
            print('='*110+'\n')
            
            #eval_env.game.round.proceed_round(eval_env.game.players, action)
            print('{} {}\n'.format(eval_env.game.round.bet_amount_cost, eval_env.game.players[eval_env.game.round.current_player].bet_cost))
            if eval_env.game.round.is_over:
                print('Toatal_stakes:{}\n'.format(eval_env.game.round.total_stakes))            
                print('Init_fund:{}\n'.format([x.init_fund for x in eval_env.game.players]))
                print('finial_fund:{}\n'.format([x.fund for x in eval_env.game.players]))
                #print('Winner: Player {}\n'.format(eval_env.game.round.winner[0].player_id))
                win_count = win_count_compute(win_count, eval_env.game.round.winner)
                win_rate = np.vstack((win_rate, win_count / i))
                diff_funds += np.asarray([x.fund - x.init_fund for x in eval_env.game.players])
                fund += np.asarray([x.fund for x in eval_env.game.players])
                plt_win_fund_rate(diff_funds.tolist(), win_rate, players)
        print('Game', i , 'Finished', sep = '-')
    # except:
    #     print('Error Game {}\n'.format(i))