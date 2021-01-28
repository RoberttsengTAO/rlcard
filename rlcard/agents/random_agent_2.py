import numpy as np
from keras.models import load_model
import os

class RandomAgent(object):
    ''' A random agent. Random agents is for running toy examples on the card games
    '''

    def __init__(self, action_num):
        ''' Initilize the random agent

        Args:
            action_num (int): the size of the ouput action space
        '''
        self.path = os.path.abspath(os.path.dirname(__file__))
        self.action_num = action_num
        self.model = load_model(self.path + '/prediction_model_alldata.h5')

    def step(self, state):
        ''' Predict the action given the curent state in gerenerating training data.

        Args:
            state (numpy.array): an numpy array that represents the current state

        Returns:
            action (int): the action predicted (randomly chosen) by the random agent
            :param self:
        '''
        # return np.random.randint(0, self.action_num)
        all_action_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        # model = load_model('prediction_model.h5')
        pred_action_list = self.model.predict(state['obs'].reshape(1, 90))
        legal_action_list = state['legal_actions']
        illegal_action = list(set(all_action_list) - set(legal_action_list))

        for i in illegal_action:
            pred_action_list[0][i] = 0

        action = self.decoder(pred_action_list)
        return action[0][0]

    def eval_step(self, state):
        ''' Predict the action given the curent state for evaluation.
            Since the random agents are not trained. This function is equivalent to step function

        Args:
            state (numpy.array): an numpy array that represents the current state

        Returns:
            action (int): the action predicted (randomly chosen) by the random agent
        '''
        return self.step(state)

    def decoder(self, output):
        output_decode = []
        for i in range(len(output)):
            output_decode.append(np.argmax(output[i]))
        return np.array(output_decode).reshape(len(output), 1)
