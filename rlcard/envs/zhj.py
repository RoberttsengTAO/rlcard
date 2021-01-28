"""
* function: extract_state, get_payoffs, decode_action
"""
import numpy as np

from rlcard.envs.env import Env
from rlcard import models
from rlcard.games.zhj.game import ZhjGame as Game
from rlcard.games.zhj.utils import ACTION_SPACE, ACTION_LIST, encode_state
from rlcard.games.zhj.card import ZhjCard


class ZhjEnv(Env):
    def __init__(self, allow_step_back=False):
        super().__init__(Game(allow_step_back), allow_step_back)
        self.state_shape = [Game.num_players * 3 + 8]

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
        legal_ids = [ACTION_SPACE[action] for action in legal_actions]
        return legal_ids

    def load_model(self):
        ''' Load pretrained/rule model

        Returns:
            model (Model): A Model object
        '''
        return models.load('zhj-nfsp')
    
