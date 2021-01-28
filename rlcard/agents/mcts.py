#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 16 10:01:58 2020

@author: robert.tseng
"""
from collections import defaultdict as ddict
from copy import deepcopy
import time
from operator import itemgetter
from math import sqrt
import numpy as np
def rollout_policy_fn(legal_action):
    action_probs = np.random.rand(len(legal_action))
    return zip(legal_action, action_probs)

def policy_value_fn(board):
    """a function that takes in a state and outputs a list of (action, probability)
    tuples and a score for the state"""
    # return uniform probabilities and 0 score for pure MCTS
    action_probs = np.ones(len(board))/len(board)
    return zip(board, action_probs), 0

class TreeNode(object):
    def __init__(self, parent, prior_p):
        self._parent = parent
        self._children = {}
        self._n_visits = 0
        self._Q = 0
        self._u = 0
        self._P = prior_p
    def select(self, c_puct):
        return max(self._children.items(), key=lambda act_node: act_node[1].get_value(c_puct))
    
    def expand(self, action_priors):
        for action, prob in action_priors:
            if action not in self._children:
                self._children[action] = TreeNode(self, prob)
    def update(self, leaf_value):
        ## Counts visit
        self._n_visits += 1
        ## Update Q 
        self._Q += (leaf_value -  self._Q) / self._n_visits
    def update_recursive(self, leaf_value):
        if self._parent:
            ## 表示 對手為輸
            self._parent.update_recursive(-leaf_value)
        self.update(leaf_value)
    def get_value(self, c_puct):
        ## UCT structure
        self._u = (c_puct * self._P * sqrt(self._parent._n_visits) /
                   (1 + self._n_visits))
        return self._Q + self._u
    def is_leaf(self):
        return self._children == {}
    def is_root(self):
        return self._parent in None
class MCTS(object):
    def __init__(self, policy_value_fn, c_puct=5, n_playout=10000):
        self._root = TreeNode(None, 1)
        self._policy = policy_value_fn
        self._c_puct = c_puct 
        self.n_playout = n_playout
    def _playout(self, game):
        node = self._root
        while True:
            if node.is_leaf():
                break
            action, node = node.select(self._c_puct)
            game.step(action)
        action_probs, _ = self._policy(game.get_legal_action())
        game_over = game.is_over()
        if not game_over:
            node.expand(action_probs)
        leaf_value = self._evaluate_rollout(game)
        node.update_recursive(-leaf_value)
    def _evaluate_rollout(self, game):
        first_player= deepcopy(game.round.current_chair)
        limit = len(game.get_legal_action())
        for i in range(limit):
            player = game.round.current_chair
            action_probs = rollout_policy_fn(game.get_legal_action())
            max_action = max(action_probs, key=itemgetter(1))[0]
            game.step(max_action)
            game_over = game.round.is_over
            if game_over:
                break
        if game.round.is_over:
            return 1 if first_player == game.round.current_chair else -1
        else:
            return 0
    def get_move(self, game):
        for _ in range(self.n_playout):
            copygame = deepcopy(game)
            self._playout(copygame)
        return max(self._root._children.items(), key = lambda act_node: act_node[1]._n_visits )[0]
    def update_with_move(self, last_move):
        if last_move in self._root._children:
            self._root = self._root._children[last_move]
            self._root._parent = None
        else:
            self._root = TreeNode(None, 1)           
    def __str__(self):
        return 'MCTS'
class MCTS_agent(object):
     """AI player based on MCTS"""
     def __init__(self, policy_value_function, c_puct=5, n_playout=2000):
        self.mcts = MCTS(policy_value_function, c_puct, n_playout)
        self.policy_value_function = policy_value_function
    
     def reset_player(self):
        self.mcts.update_with_move(-1)
     def eval_step(self, state):
        game = state['game']
        sensible_moves = game.get_legal_action()
        # the pi vector returned by MCTS as in the alphaGo Zero paper
        if len(sensible_moves) > 0:
            move = self.mcts.get_move(game)
            self.mcts.update_with_move(-1)
            return move
        else:
            print("WARNING: the board is full")
     def step(self, state):
        game = state['game']
        sensible_moves = game.get_legal_action()
        # the pi vector returned by MCTS as in the alphaGo Zero paper
        if len(sensible_moves) > 0:
            move = self.mcts.get_move(game)
            self.mcts.update_with_move(-1)
            return move
        else:
            print("WARNING: the board is full")   
         
     def get_action(self, game):
        sensible_moves = game.get_legal_action()
        # the pi vector returned by MCTS as in the alphaGo Zero paper
        if len(sensible_moves) > 0:
            move = self.mcts.get_move(game)
            self.mcts.update_with_move(-1)
            return move
        else:
            print("WARNING: the board is full")
    
# mcts = MCTS(policy_value_fn, 5, 20)
# copygame = deepcopy(game)
# mcts._playout(copygame)
# mcts.get_move(game)
# k = map(lambda act_node: (act_node[1]._n_visits ,act_node[1]._Q), mcts._root._children.items())
