from rlcard.games.holdem.judger import holdemJudger
from collections import Counter
from functools import reduce
import re
class holdemRound(object):
    def __init__(self, dealer, num_players, small_blind_amount):
        """ Initialize the round class

        Args:
            dealer (object): the object of holdemDealer
            num_players (int): the number of players in game
        """
        self.small_blind_amount = small_blind_amount
        self.bet_amount_cost = 2*small_blind_amount
        self.dealer = dealer
        self.count = 1
        self.current_player = 2 % num_players
        self.num_players = num_players
        self.is_over = False
        self.all_in_num = 0
        self.all_in_money = 0
        self.first_all_in_player_id = None
        self.first_raise = 0
        self.total_stakes = [small_blind_amount, 2*small_blind_amount]+[0]*(num_players-2)
        self.winner = None
    def proceed_round(self, players, action):
        # action cost
        cost = 0
        be_bet_cost = players[self.current_player].bet_cost
        # Foolproof
        if action not in ['check', 'all-in', 'fold'] and not bool(re.match('raise-\d', action)):
            return('Action was typed error')
        if action == 'check':
            players[self.current_player].check_count += 1
            cost = self.bet_amount_cost - be_bet_cost
            # print(cost)
            if cost >= players[self.current_player].fund:
                cost = players[self.current_player].fund
                players[self.current_player].all_in = True
        elif 'raise' in action:
            players[self.current_player].raise_count += 1
            _, money = action.split('-')
            self.bet_amount_cost = int(money)
            self.first_raise = 1
            cost = self.bet_amount_cost - be_bet_cost
            list(map(lambda x: x.reset(), players))
        elif action == 'all-in':
            cost = players[self.current_player].fund 
            self.bet_amount_cost = cost + be_bet_cost
            if self.all_in_num == 0:
                self.first_all_in_player_id = self.current_player
                list(map(lambda x: x.reset(), players))
            players[self.current_player].all_in = True
            self.all_in_num = 1
        elif action == 'fold':
            players[self.current_player].die()
            # if self.count == 1:
            #     if self.current_player == 0 and be_bet_cost == 0:
            #         cost = self.small_blind_amount
            #     elif self.current_player == 1 and be_bet_cost == 0:
            #         cost = 2*self.small_blind_amount
                    
        players[self.current_player].check = True
        self.total_stakes[self.current_player] += int(cost)
        players[self.current_player].fund = players[self.current_player].fund - cost
        players[self.current_player].bet_cost = self.bet_amount_cost
        # next player
        self.current_player = (self.current_player+1) % self.num_players
        check_list = list(map(lambda x: x.check, players))
        n = 1
        num = self.num_players
        while (players[self.current_player].fold or players[self.current_player].all_in)\
            and not n == num:
            # print(self.current_player,\
            #       players[self.current_player].fold, players[self.current_player].all_in,\
            #       players[self.current_player].fold or players[self.current_player].all_in)
            players[self.current_player].check = True
            self.current_player = (self.current_player + 1) % self.num_players
            check_list = list(map(lambda x: x.check, players))
            n += 1
        # compute states of players
        check_fold_list = list(map(lambda x: 1 if x.check | x.fold else 0, players))
        no_fold_count = list(map(lambda x: 0 if x.fold else 1, players))
        check_fold_all_list = list(map(lambda x: x.check | x.fold | x.all_in,players))
        all_in_count = list(map(lambda x: 1 if x.all_in else 0, players))
        all_in_fold_list = list(map(lambda x: 1 if x.all_in | x.fold else 0, players))
        if sum(all_in_count) == sum(no_fold_count) or sum(no_fold_count) == 1 \
            or (self.count == 4 and all(check_fold_all_list)) \
            or sum(all_in_fold_list) == num - 1 and sum(check_fold_list) == num:
            self.winner = self.judge(players)
        else:
            # compute states of players
            # check_count = list(map(lambda x: 1 if x.check else 0, players))
            # no_fold_count = list(map(lambda x: 0 if x.fold else 1, players))
            # check_fold_list = list(map(lambda x: x.check | x.fold, players))
            # all_in_count = list(map(lambda x: 1 if x.all_in else 0, players))
            
            # new round
            if all(check_fold_all_list):
                [x.all_reset() for x in players]
                self.bet_amount_cost = 0
                self.count += 1
                self.first_raise = 0
                self.current_player = 0
                while players[self.current_player].fold or players[self.current_player].all_in:
                    players[self.current_player].check = True
                    self.current_player = (self.current_player + 1) % self.num_players
        return players
    def get_legal_actions(self, players, player_id):
        legal_actions = ['check']
        need_add_cost = self.bet_amount_cost - players[player_id].bet_cost
        if not players[player_id].all_in:
            legal_actions.append('fold')
        if need_add_cost < players[player_id].fund:
            legal_actions.append('all-in')
        if (self.bet_amount_cost + need_add_cost) < players[player_id].fund \
            and 2*self.small_blind_amount < players[player_id].fund:
            if self.first_raise == 0 and self.count != 1:
                min1= str(2*self.small_blind_amount)
            else:
                min1= str(int(self.bet_amount_cost) + 2*self.small_blind_amount)
            mod = (players[player_id].fund - self.bet_amount_cost) // (2*self.small_blind_amount)
            max1 = str(int(self.bet_amount_cost)+ mod * 2*self.small_blind_amount)
            legal_actions.append('raise-'+min1+'-'+max1)
        return legal_actions
    
    def judge(self, players):
        winner = holdemJudger.compare_winner(players)
        # pot setting  
        pot = holdemJudger.split_pot(players, self.total_stakes)
        for sub_pot in pot:
            stacks = sub_pot['amount']
            eligibles_player = sub_pot['eligibles']
            eligibles_winner, eligibles_loser = holdemJudger.judge_winner(eligibles_player)
            n = len(eligibles_winner)
            if n != 1:
                for eligible_winner in eligibles_winner:
                    eligible_winner.fund +=  int(stacks / n)
            else:
                eligibles_winner[0].fund += stacks
        self.is_over = True
        return winner 
        
        
            
            
        
        