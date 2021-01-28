#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct  8 14:01:21 2020

@author: robert.tseng
"""
from rlcard.envs.env import Env
from rlcard.games.gobang.game import gobangGame as Game
from copy import deepcopy
import numpy as np
class gobangEnv(Env):
    def __init__(self, board_size = [15, 15], win_count = 5):
        super().__init__(Game(board_size, win_count))
        self.state_shape = board_size[0] * board_size[1]

    def extract_state(self, state):
        legal_action_id = self.get_legal_actions()
        extrated_state = {'obs': np.asarray(state).flatten(), 'legal_actions': legal_action_id,
                          'game_legal_actions':self.game.get_legal_action(),
                          'game': deepcopy(self.game)}
        return extrated_state

    def get_payoffs(self):
        return self.game.get_payoffs()

    def decode_action(self, action_id):
        return action_id
    
    def get_legal_actions(self):
        legal_actions = list(self.game.get_legal_action().keys())
        return legal_actions
    
    
    
