#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  5 12:20:14 2020

@author: robert.tseng
"""
from rlcard.games.gobang.judger import gobangJudger
class gobangRound(object):
    def __init__(self, board_size, win_count):
        self.current_chair = 0
        self.game_end = [0, 0]
        self.is_over = False
        self.board_size = board_size
        self.legal_actions = {}
        self.win_count = win_count
        k = 0
        for i in range(board_size[0]):
            for j in range(board_size[1]):
                self.legal_actions[k] = (i, j)
                k += 1
    def proceed_round(self, board, action):
        chair = self.current_chair + 1
        board_size = self.board_size
        win_count = self.win_count
        ## set chess
        row, col = self.legal_actions[action]
        board[row][col] = chair
        self.legal_actions.pop(action, None)
        is_over = self.judge(board, [row, col], win_count, board_size, chair)
        full_board = True if len(self.legal_actions) == 0 else False
        if is_over:
            self.is_over = True
            self.game_end[chair-1] = 1
            self.game_end[chair%2] = -1
        elif full_board:
            self.is_over = True
        else:
            self.current_chair = chair % 2
        return board
    def get_legal_action(self):
        return self.legal_actions
        
    def judge(self,  board, action, win_count, board_size, chair):
        v_c = gobangJudger.v_check(board, action, win_count, board_size, chair)
        h_c = gobangJudger.h_check(board, action, win_count, board_size, chair)
        ls_c = gobangJudger.ls_check(board, action, win_count, board_size, chair)
        rs_c = gobangJudger.rs_check(board, action, win_count, board_size, chair)
        max_count = max([v_c, h_c, ls_c, rs_c])
        if max_count >= win_count:
            return True
        else:
            return False
