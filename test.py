#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  6 11:11:10 2020

@author: robert.tseng
"""
import os
os.chdir('/Users/robert.tseng/Documents/RL_test')
from copy import deepcopy
from rlcard.games.holdem.dealer import holdemDealer
from rlcard.games.holdem.player import holdemPlayer
from rlcard.games.holdem.round import holdemRound
from rlcard.games.holdem.game import holdemGame
from rlcard.games.holdem.card import computer_power
import numpy as np
import sys
import re
import time
open_num = [0, 0, 3, 4, 5]
f = open('/Users/robert.tseng/Documents/RL_test/test.log', 'w')
if __name__ == '__main__':
    # num_players= int(sys.argv[1])
    # small_bet = int(sys.argv[2])
    num_players = 6
    small_bet = 10
    game_count = 0
    com = computer_power()
    game = holdemGame(num_players=num_players, allow_step_back=False, small_blind_amount= small_bet)
    for i in range(100000):
        try:
            game.init_game()
            set_human = np.random.choice(range(num_players))
            comm_list = [i.suit_str + i.number_str for i in game.community]
            community = ' '.join(comm_list)
            f.write('Game starting time:'+ time.ctime()+'\n')
            f.write('Setting game community card: {}\n'.format(community))
            print('Game starting time:'+ time.ctime()+'\n')
            print('Setting game community card: {}\n'.format(community))
            player_id = 0
            for player in game.players:
                hand = ' '.join([j.suit_str + j.number_str for j in player.hand])
                power = com.eval_hand(player.hand, game.community)
                f.write('Player {} hand card: {} and power: {} win_rate: {} \n'.format(str(player_id), hand, str(power), player.win_rate))
                print('Player {} hand card: {} and power: {} win_rate: {} \n'.format(str(player_id), hand, str(power), player.win_rate))
                player_id += 1
            print('Human_set:{}\n'.format(str(set_human)))
            print('-'*30)
            f.write('Human_set:{}\n'.format(str(set_human)))
            f.write('-'*30)
            while not game.round.is_over:
                if game.round.count != game_count:
                    f.write('='*50 + 'Round:{}'.format(game.round.count) + '='*50+'\n')
                    f.write('='*30 + 'Open card:{}\n'.format(comm_list[:open_num[game.round.count]]))
                    print('='*50 + 'Round:{}'.format(game.round.count) + '='*50+'\n')
                    print('='*30 + 'Open card:{}\n'.format(comm_list[:open_num[game.round.count]]))
                    game_count = game.round.count 
                f.write('{} {}\n'.format(game.round.total_stakes, 
                      game.round.current_player,game.players[game.round.current_player].fund))
                print('{} {}\n'.format(game.round.total_stakes, 
                      game.round.current_player,game.players[game.round.current_player].fund))
                actions = game.round.get_legal_actions(game.players, game.round.current_player)
                f.write('legal_action:' + ' '.join(actions)+'\n')
                print('legal_action:' + ' '.join(actions)+'\n')
                if game.round.current_player != set_human:
                    action = np.random.choice(actions)
                    if re.match('raise', action):
                        act, min1, max1 = action.split('-')
                        stack = str(np.random.choice(range(int(min1), int(max1)+2*small_bet, 2*small_bet)))
                        action = act+'-'+stack
                else:
                    action = input('Action:')
                f.write('{} execute {}\n'.format(str(game.round.current_player), action))
                f.write('='*110+'\n')
                print('{} execute {}\n'.format(str(game.round.current_player), action))
                print('='*110+'\n')
                game.round.proceed_round(game.players, action)
                f.write('{} {}\n'.format(game.round.bet_amount_cost, game.players[game.round.current_player].bet_cost))
                print('{} {}\n'.format(game.round.bet_amount_cost, game.players[game.round.current_player].bet_cost))
                if game.round.is_over:
                    f.write('Toatal_stakes:{}\n'.format(game.round.total_stakes))            
                    f.write('Init_fund:{}\n'.format([x.init_fund for x in game.players]))
                    f.write('finial_fund:{}\n'.format([x.fund for x in game.players]))
                    f.write('Winner: Player {}\n'.format(game.round.winner[0].player_id))
                    print('Toatal_stakes:{}\n'.format(game.round.total_stakes))            
                    print('Init_fund:{}\n'.format([x.init_fund for x in game.players]))
                    print('finial_fund:{}\n'.format([x.fund for x in game.players]))
                    print('Winner: Player {}\n'.format(game.round.winner[0].player_id))
            f.write('Game'+str(i)+'Finished')
            print('Game', i , 'Finished', sep = '-')
        except:
            f.write('Error Game {}\n'.format(i))
            print('Error Game {}\n'.format(i))
            continue
    f.close()
