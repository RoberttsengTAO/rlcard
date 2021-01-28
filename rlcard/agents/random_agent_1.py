from random import sample


class RandomAgent(object):
    ''' A random agent. Random agents is for running toy examples on the card games
    '''

    def __init__(self, action_num):
        ''' Initilize the random agent

        Args:
            action_num (int): the size of the ouput action space
        '''
        self.action_num = action_num

    def step(self, state):
        ''' Predict the action given the curent state in gerenerating training data.

        Args:
            state (numpy.array): an numpy array that represents the current state

        Returns:
            action (int): the action predicted (randomly chosen) by the random agent
        '''
        # return np.random.randint(0, self.action_num)
        action_dict = {"check": 0, "fold": 1, "all-in": 2, "raise-1": 3, "raise-2": 4, "raise-3": 5, "raise-4": 6,
                       "raise-10": 7, "raise-20": 8,
                       "raise-50": 9, "raise-100": 10, "raise-200": 11}

        win_rate = state['obs'][-8]
        cur_chair = state['obs'][-1]
        # get round info
        open_card = sum(state['obs'][30:82]) - 2
        # round 1
        if open_card == 0:
            if win_rate > 0.16 or win_rate - self.compute_bet_ratio(state) > 0:
                return action_dict['check']
            else:
                return action_dict['fold']
        else:
            bet_ratio = self.compute_bet_ratio(state)
            gap = win_rate - bet_ratio
            if gap < 0:
                return action_dict['fold']  # fold index
            else:
                all_moves = state['legal_actions']
                print(all_moves)

                if win_rate > 0.8:
                    if action_dict['all-in'] in all_moves:
                        return action_dict['all-in']
                    else:
                        return action_dict['check']
                else:
                    if action_dict['fold'] in all_moves:
                        all_moves.remove(action_dict['fold'])
                    if action_dict['fold'] in all_moves:
                       all_moves.remove(action_dict['check'])
                    return sample(all_moves, 1)[0]

    # return np.random.choice(state['legal_actions'])

    def eval_step(self, state):
        ''' Predict the action given the current state for evaluation.
            Since the random agents are not trained. This function is equivalent to step function

        Args:
            state (numpy.array): an numpy array that represents the current state

        Returns:
            action (int): the action predicted (randomly chosen) by the random agent
        '''

        return self.step(state)

    def compute_bet_ratio(self, state):
        cur_chair = int(state['obs'][-1])
        all_stakes = state['obs'][-7:-1]
        self_stake = all_stakes[cur_chair]
        cur_bet = max(all_stakes) - self_stake
        return cur_bet / sum(all_stakes)
