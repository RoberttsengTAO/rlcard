from copy import deepcopy

from rlcard.games.zhj.dealer import ZhjDealer
from rlcard.games.zhj.player import ZhjPlayer
from rlcard.games.zhj.round import ZhjRound


class ZhjGame(object):
    num_players = 6

    def __init__(self, allow_step_back=False):
        self.allow_step_back = allow_step_back
        self.payoffs = [0 for _ in range(self.num_players)]

    def init_game(self):
        """ Initialize players and state

        Returns:
            (tuple): Tuple containing:

                (dict): The first state in one game
                (int): Current player's id
        """
        # Initalize payoffs
        self.payoffs = [0 for _ in range(self.num_players)]

        # Initialize a dealer that can deal cards
        self.dealer = ZhjDealer()

        # Initialize a Round
        self.round = ZhjRound(self.dealer, self.num_players)

        # Initialize four players to play the game
        base_fund = 100
        self.players = [ZhjPlayer(i, base_fund) for i in range(self.num_players)]
        self.init_fund = [base_fund for _ in range(self.num_players)]

        # Deal 3 cards to each player to prepare for the game
        for player in self.players:
            self.dealer.deal_cards(player, 3)

        # Save the hisory for stepping back to the last state.
        self.history = []

        self.round.start_game(self.players)
        player_id = self.round.current_player
        state = self.get_state(player_id)
        return state, player_id

    def step(self, action):
        """ Get the next state

        Args:
            action (str): A specific action

        Returns:
            (tuple): Tuple containing:

                (dict): next player's state
                (int): next plater's id
        """

        if self.allow_step_back:
            # First snapshot the current state
            his_dealer = deepcopy(self.dealer)
            his_round = deepcopy(self.round)
            his_players = deepcopy(self.players)
            self.history.append((his_dealer, his_players, his_round))

        self.players = self.round.proceed_round(self.players, action)

        player_id = self.round.current_player
        state = self.get_state(player_id)

        return state, player_id

    def step_back(self):
        """ Return to the previous state of the game

        Returns:
            (bool): True if the game steps back successfully
        """
        if not self.history:
            return False
        self.dealer, self.players, self.round = self.history.pop()
        return True

    def get_state(self, player_id):
        """ Return player's state

        Args:
            player_id (int): player id

        Returns:
            (dict): The state of the player
        """
        state = {}
        # game info
        state['players_fund'] = [i.fund for i in self.players]
        state['players_fold'] = [i.fold for i in self.players]
        state['players_check'] = [i.check for i in self.players]
        state['cur_bet_level'] = self.round.current_bet_level
        state['total_stakes'] = self.round.total_stakes
        state['player_size'] = self.num_players
        state['all_in_num'] = self.round.all_in_num
        state['all_in_money'] = self.round.all_in_money
        # player info
        player = self.players[player_id]
        state['player'] = player_id
        state['init fund'] = player.init_fund
        state['fund'] = player.fund
        state['fold'] = player.fold
        state['check'] = player.check
        # after check, know
        state['hand'] = [str(i) for i in player.hand]
        state['power'] = player.power

        # legal actions
        state['legal_actions'] = self.round.get_legal_actions(self.players, player_id)

        return state

    def get_payoffs(self):
        """ Return the payoffs(reward) of the game

        Returns:
            (list): Each entry corresponds to the payoff of one player
        """
        # reward = []
        # for i in self.payoffs:
        #     if i >= 0:
        #         reward.append(1)
        #     elif i >= -(self.round.bet_option[-1] * 2 + 1):
        #         reward.append(0)
        #     else:
        #         reward.append(-1)
        # 
        # return reward
        return self.payoffs

    def get_legal_actions(self):
        """ Return the legal actions for current player

        Returns:
            (list): A list of legal actions
        """

        return self.round.get_legal_actions(self.players, self.round.current_player)

    def get_player_num(self):
        """ Return the number of players in Limit Texas Hold'em

        Returns:
            (int): The number of players in the game
        """
        return self.num_players

    @staticmethod
    def get_action_num():
        """ Return the number of applicable actions

        Returns:
            (int): The number of actions. There are 15 actions
        """
        return 15

    def get_player_id(self):
        """ Return the current player's id

        Returns:
            (int): current player's id
        """
        return self.round.current_player

    def is_over(self):
        """ Check if the game is over

        Returns:
            (boolean): True if the game is over
        """
        #self.payoffs = [(player.fund - player.init_fund)/player.init_fund for player in self.players]
        self.payoffs = [(player.fund - player.init_fund) for player in self.players]
        return self.round.is_over


# For test
if __name__ == '__main__':
    import pprint
    import random

    game = ZhjGame()
    game.init_game()
    while not game.is_over():
        print('=' * 30)
        pprint.pprint(game.get_state(game.round.current_player))
        # action = input('your action :')
        action = random.sample(game.get_legal_actions(), 1)[0]
        print(action)
        game.step(action)
    pprint.pprint(game.get_state(game.round.current_player))
    print(game.payoffs)
    print('*' * 30)
