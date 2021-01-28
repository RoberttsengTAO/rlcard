#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  5 11:27:17 2020

@author: robert.tseng
"""

from rlcard.games.gobang.player import gobangplayer
from rlcard.games.gobang.round import gobangRound
class gobangGame(object):
    def __init__(self, board_size = [15, 15], win_count = 5):
        self.board_size = board_size
        self.win_count = win_count
        self.num_players = 2
    def init_game(self):
        ## setting board 
        board_size = self.board_size
        column_board = [0]*board_size[1]
        board = [column_board.copy() for _ in range(board_size[0])]
        self.board = board
        ## setting player 
        players = [gobangplayer(i) for i in range(2)]
        self.round = gobangRound(self.board_size, self.win_count)
        self.players = players
        return board, self.round.current_chair
    def step(self, action):
        board = self.round.proceed_round(self.board, action)
        self.board = board
        chair = self.round.current_chair+1
        state = self.board
        return board, self.round.current_chair
    def get_state(self, player_id):
        return self.board
    def get_legal_action(self):
        return self.round.get_legal_action()
    def get_payoffs(self):
        return self.payoffs
    def is_over(self):
        self.payoffs = self.round.game_end
        return self.round.is_over
    def get_player_id(self):
        return self.round.current_chair
    def get_player_num(self):
        """ Return the number of players in Limit Texas Hold'em
    
        Returns:
        (int): The number of players in the game
        """
        return self.num_players
    def get_action_num(self):
        """ Return the number of applicable actions

        Returns:
            (int): The number of actions. There are 15 actions
        """
        return self.board_size[0]*self.board_size[1]