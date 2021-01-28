#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 12 10:45:13 2020

@author: robert.tseng
"""


import os
#os.chdir('/Users/robert.tseng/Documents/fix_version/holdem_game')
from copy import deepcopy
import rlcard
import tensorflow as tf
from rlcard.envs.gobang import gobangEnv
from rlcard.games.gobang.player import gobangplayer
from rlcard.games.gobang.round import gobangRound
from rlcard.games.gobang.game import gobangGame
from rlcard.agents.random_agent import RandomAgent as ragent
from rlcard.agents.ac_agent import A2Cagent 
from rlcard.agents.mcts import MCTS_agent as mcts_agent
from rlcard.agents.mcts import policy_value_fn
from copy import deepcopy
# =============================================================================
# Game setting 
# =============================================================================
def printBoard(board):
    for i in range(len(board)):
        for j in range(len(board[i])):
            ele = board[i][j]
            if ele == 0:
                ele = ' '
            elif ele == 1:
                ele = 'x'
            else:
                ele = 'o'
            if j == 0:
                print('|'+ele, end = '|')
            else:
                print(ele, end = '|')
        print('')
        
        
eval_env = gobangEnv([7, 7], 5)
state_size = eval_env.state_shape
action_size = eval_env.action_num
sess = tf.Session()
agents = [A2Cagent(sess, state_size, action_size, actor_lr = 0.01, critic_lr = 0.01, discount_factor=.8),
          mcts_agent(policy_value_fn, 5, 2000)]
eval_env.set_agents(agents)
# eval_env.init_game()
# game = deepcopy(eval_env.game)

if __name__ == '__main__':
    num_players= eval_env.player_num
    # small_bet = int(sys.argv[2])
    # try:
    for i in range(1, 1001):
        # try:
        game_count = 0
        state, player_id = eval_env.init_game() 
        printBoard(state['obs'])
        while not eval_env.game.round.is_over :
            if len(eval_env.game.get_legal_action()) == 0:
                break
            if eval_env.game.round.current_chair == 0: 
                action = eval_env.agents[eval_env.game.round.current_chair].eval_step(state)
            else:
                game = deepcopy(eval_env.game)
                action = eval_env.agents[eval_env.game.round.current_chair].get_action(game)
            legal = eval_env.game.get_legal_action()
            print(eval_env.game.round.current_chair)
            print(action, legal[action])
            # if eval_env.game.round.current_player == 1:
            next_state, next_player_id = eval_env.step(action)
            print(next_player_id)
            state = next_state
            print('='*33)
            printBoard(state['obs'])
            print('='*33)
            #eval_env.game.round.proceed_round(eval_env.game.players, action)
            #print('{} {}\n'.format(eval_env.game.round.bet_amount_cost, eval_env.game.players[eval_env.game.round.current_player].bet_cost))
            if eval_env.game.round.is_over:
                print('OK')
            
        time.sleep(1)
        print('Game', i , 'Finished', sep = '-')
        
mcts = eval_env.agents[eval_env.game.round.current_chair]
