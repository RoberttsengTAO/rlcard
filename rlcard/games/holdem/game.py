from copy import deepcopy

from rlcard.games.holdem.dealer import holdemDealer, estimate_hole_card_win_rate
from rlcard.games.holdem.player import holdemPlayer
from rlcard.games.holdem.round import holdemRound

class holdemGame(object):

    def __init__(self, num_players=6, allow_step_back=False, small_blind_amount = 10):
        self.num_players = num_players
        self.allow_step_back = allow_step_back
        self.payoffs = [0]*self.num_players
        self.bet_cost = [0]*self.num_players
        self.small_blind_amount = small_blind_amount
    def init_game(self):
        """ Initialize players and state

        Returns:
            (tuple): Tuple containing:

                (dict): The first state in one game
                (int): Current player's id
        """
        # Initalize payoffs
        num_players = self.num_players
        self.payoffs = [0 for _ in range(self.num_players)]
        small_blind_amount = self.small_blind_amount
        # Initialize a dealer that can deal cards
        self.dealer = holdemDealer()

        # Initialize a Round
        self.round = holdemRound(self.dealer, self.num_players, small_blind_amount)
        # Initialize four players to play the game
        base_fund = 200*small_blind_amount
        self.players = [holdemPlayer(i, base_fund, small_blind_amount) for i in range(self.num_players)]
        self.players[0].fund -= small_blind_amount
        self.players[0].bet_cost += small_blind_amount
        self.players[1].fund -= 2*small_blind_amount
        self.players[1].bet_cost += 2*small_blind_amount
        self.init_fund = [self.players[i].init_fund for i in range(self.num_players)]
        open_card = [0, 3, 4, 5]
        # Deal 2 cards to each player to prepare for the game
        for player in self.players:
            self.dealer.deal_cards(player, 2)
        
        self.community = self.dealer.deal_community()
        # Compute power 
        for player in self.players:
            self.dealer.computer_power(player, self.community)
            for i in range(4):
                if i == 0:
                    community = None
                else:
                    community = self.community[:open_card[i]]
                player.win_rate[i] = estimate_hole_card_win_rate(500, \
                                    num_players, player.hand, community)
        # Save the hisory for stepping back to the last state.
        self.history = []
        player_id = self.round.current_player
        state = self.get_state(player_id)
        return state, player_id
        #self.round.start_game(self.players)
        #player_id = self.round.current_player
        #state = self.get_state(player_id)
        #return state, player_id

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
        if 'raise' in action:
            action, per = action.split('-')
            # raise_action = [sub_action for sub_action in self.get_legal_actions() \
            #                 if 'raise' in sub_action]
            # _, min1, max1 = raise_action[0].split('-')
            action = 'raise-' + str(2*int(per)*self.small_blind_amount)
        
        self.players = self.round.proceed_round(self.players, action)
        # self.round.proceed_round(self.players, action)
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
        players = self.players
        players = players[player_id:] + players[:player_id]
        player_init_fund = max([player.init_fund for player in players])
        state['players_fund'] = [i.fund / player_init_fund  for i in players]
        state['total_stakes'] = self.round.total_stakes
        state['total_stakes'] = state['total_stakes'][player_id:] + state['total_stakes'][:player_id] 
        state['total_stakes'] = [ state['total_stakes'][i] / player_init_fund for i in range(len(players))]
        
        state['players_fold'] = [i.fold for i in players]
        state['players_raise_count'] = [i.raise_count for i in players]
        state['players_check_count'] = [i.check_count for i in players]
        state['players_check'] = [i.check for i in players]
        state['player_size'] = self.num_players
        state['all_in'] = [i.all_in for i in players]
        # player info
        player = self.players[player_id]
        state['player'] = player_id
        # after check, know
        state['hand_suit'] = [i.suit for i in player.hand]
        state['hand_rank'] = [i.rank for i in player.hand]
        state['round'] = self.round.count
        open_card = [0, 3, 4, 5]
        open_card_class = self.community[:open_card[self.round.count-1]]
        state['community_suit'] = [i.suit for i in open_card_class]
        state['community_rank'] = [i.rank for i in open_card_class]
        state['power'] = player.power
        state['win_rate'] = player.win_rate     
        state['round'] = self.round.count          
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
        self.payoffs = [(player.fund - player.init_fund) / 2*self.small_blind_amount for player in self.players]
        return self.round.is_over


# For test
# if __name__ == '__main__':
#     import pprint
#     import random

#     game = holdemGame()
#     game.init_game(1)
#     while not game.is_over():
#         print('=' * 30)
#         pprint.pprint(game.get_state(game.round.current_player))
#         # action = input('your action :')
#         action = random.sample(game.get_legal_actions(), 1)[0]
#         print(action)
#         game.step(action)
#     pprint.pprint(game.get_state(game.round.current_player))
#     print(game.payoffs)
#     print('*' * 30)
#    game = holdemGame()
#    game.init_game(1)
#    while not game.round.is_over :
#        print(game.round.is_over, game.round.count, game.round.total_stakes, 
#              game.round.current_player,game.players[game.round.current_player].fund[0])
#        actions = game.round.get_leagl_actions(game.players, game.round.current_player)
#        action = np.random.choice(actions)
#        print('{} execute {}'.format(str(game.round.current_player), action))
#        game.round.proceed_round(game.players, action)
#    print([x.fold for x in game.players])
#    while game.round.is_over == False:
#        game.round.proceed_round(game.players, 'check')
#        print(game.round.count, game.round.total_stakes, game.round.current_player)
#    print(game.round.is_over)
#    game.round.total_stakes
#    game.round.check_state
###  fix all_reset()
### 