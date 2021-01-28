#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  5 12:06:12 2020

@author: robert.tseng
"""


class gobangJudger(object):
    @staticmethod
    def v_check( board, action, win_count, board_size, chair):
        v_c = 1
        max_row, max_col = board_size
        row, col = action
        right_d_cont = True
        left_d_cont = True
        step = 1
        chess_chair = board[row][col]
        while True:
            if left_d_cont and col-step > 0 and board[row][col-step] == chair:
                v_c += 1 
            else:
                left_d_cont = False
            if right_d_cont and col + step < max_col and  board[row][col+step] == chair:
                v_c += 1
            else:
                right_d_cont = False
            step += 1
            if v_c >= win_count or (left_d_cont or right_d_cont) == False:
                return v_c
    @staticmethod
    def h_check(board, action, win_count, board_size, chair):
        h_c = 1
        max_row, max_col = board_size
        row, col = action
        right_d_cont = True
        left_d_cont = True
        step = 1
        chess_chair = board[row][col]
        while True:
            if left_d_cont and row-step > 0 and board[row-step][col] == chair:
                h_c += 1 
            else:
                left_d_cont = False
            if right_d_cont and row + step < max_row and  board[row+step][col] == chair:
                h_c += 1
            else:
                right_d_cont = False
            step += 1
            if h_c >= win_count or (left_d_cont or right_d_cont) == False:
                return h_c
    @staticmethod
    def ls_check(board, action, win_count, board_size, chair):
        ls_c = 1
        max_row, max_col = board_size
        row, col = action
        right_d_cont = True
        left_d_cont = True
        step = 1
        chess_chair = board[row][col]
        while True:
            if left_d_cont and row-step > 0 and col + step < max_col \
                and board[row-step][col+step] == chair:
                ls_c += 1 
            else:
                left_d_cont = False
            if right_d_cont and row + step < max_row and col - step > 0 \
                and  board[row+step][col-step] == chair:
                ls_c += 1
            else:
                right_d_cont = False
            step += 1
            if ls_c >= win_count or (left_d_cont or right_d_cont) == False:
                return ls_c
    @staticmethod
    def rs_check(board, action, win_count, board_size, chair):
        rs_c = 1
        max_row, max_col = board_size
        row, col = action
        right_d_cont = True
        left_d_cont = True
        step = 1
        chess_chair = board[row][col]
        while True:
            if left_d_cont and col-step > 0 and row + step < max_row \
                and board[row+step][col-step] == chair:
                rs_c += 1 
            else:
                left_d_cont = False
            if right_d_cont and col + step < max_row and row - step > 0 \
                and  board[row-step][col+step] == chair:
                rs_c += 1
            else:
                right_d_cont = False
            step += 1
            if rs_c >= win_count or (left_d_cont or right_d_cont) == False:
                return rs_c