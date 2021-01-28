"""
* function: extract_state, get_payoffs, decode_action
"""
import numpy as np
import os 
from rlcard.envs.env import Env
from rlcard import models
from rlcard.games.holdem.game import holdemGame as Game
from rlcard.games.holdem.utils import ACTION_SPACE, ACTION_LIST, encode_state
from rlcard.games.holdem.card import holdemCard
class holdemEnv(Env):
    def __init__(self, num_players=6, allow_step_back=False):
        super().__init__(Game(num_players, allow_step_back), allow_step_back)
        self.state_shape = [num_players * 6 + 54]

    def extract_state(self, state):
        obs = encode_state(state)
        legal_action_id = self.get_legal_actions()
        extrated_state = {'obs': obs, 'legal_actions': legal_action_id}
        return extrated_state

    def get_payoffs(self):
        return self.game.get_payoffs()

    def decode_action(self, action_id):
        legal_ids = self.get_legal_actions()
        if action_id in legal_ids:
            return ACTION_LIST[action_id]
        return ACTION_LIST[np.random.choice(legal_ids)]

    def get_legal_actions(self):
        legal_actions = self.game.get_legal_actions()
        big_blind_amount = 2*self.game.round.small_blind_amount
        # legal_actions = game.get_legal_actions()
        # big_blind_amount = 2*game.round.small_blind_amount
        actions_map = [ actions for actions in legal_actions if 'raise' in actions]
        if actions_map:
            _, min1, max1 = actions_map[0].split('-')
            min_ratio = int(min1) // big_blind_amount
            max_ratio = int(max1) // big_blind_amount
            raise_action = [action for action in  ACTION_LIST[3:] 
                if int(action.split('-')[1]) >= min_ratio 
                and  int(action.split('-')[1]) <= max_ratio] 
            legal_actions_1 = ACTION_LIST[:3] + raise_action
        else:
            legal_actions_1 = legal_actions            
        legal_ids = [ACTION_SPACE[action] for action in legal_actions_1]
        return legal_ids

    # def load_model(self):
    #     ''' Load pretrained/rule model

    #     Returns:
    #         model (Model): A Model object
    #     '''
    #     return models.load('zhj-nfsp')



