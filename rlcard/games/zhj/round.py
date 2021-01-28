from rlcard.games.zhj.judger import ZhjJudger


class ZhjRound(object):
    def __init__(self, dealer, num_players):
        """ Initialize the round class

        Args:
            dealer (object): the object of ZhjDealer
            num_players (int): the number of players in game
        """
        self.current_bet_level = 0
        self.bet_option = [1, 2, 5, 10]
        self.dealer = dealer
        self.count = 1
        self.current_player = 0
        self.num_players = num_players
        self.is_over = False
        self.all_in_num = 0
        self.all_in_money = 0
        self.first_all_in_player_id = None
        self.total_stakes = 0

    def proceed_round(self, players, action):
        """ Call other Classes's functions to keep one round running

        Args:
            players (list): object of ZhjPlayer
            action (str): string of legal action
        """
        if action == 'call':
            cost = self.bet_option[self.current_bet_level]
        elif 'raise' in action:
            cost = self.bet_option[int(action.split('-')[1])]
        elif action == 'all in':
            if self.all_in_num:
                cost = self.all_in_money
            else:
                cost = min([player.fund for player in players if not player.fold])
        elif 'compare' in action:
            cost = self.bet_option[self.current_bet_level] * 2
        else:
            cost = 0

        # after check, cost * 2
        if action != 'all in' and players[self.current_player].check:
            cost *= 2

        init_player_id = self.current_player
        players[self.current_player].fund -= cost
        self.total_stakes += cost
        if action == 'fold':
            players[self.current_player].die()
        elif action == 'check':
            players[self.current_player].check = True
        elif action == 'all in':
            if not self.all_in_num:
                self.first_all_in_player_id = self.current_player
                self.all_in_money = cost
            self.all_in_num += 1
        elif 'raise' in action:
            self.current_bet_level = int(action.split('-')[1])
        elif 'compare' in action:
            compared_player_id = int(action.split('-')[1])
            _, loser = ZhjJudger.judge_winner([players[self.current_player], players[compared_player_id]])
            loser[0].die()

        # check game done
        live_players = [i for i in players if not i.fold]
        if len(live_players) == 1:
            self.is_over = True
            live_players[0].fund += self.total_stakes
            self.total_stakes = 0
            return players

        # check all live player all in
        if sum([1 for i in players if not i.fold]) == self.all_in_num:
            self.all_compare(players=players, all_in_state=True)

        # change index
        if action != 'check':
            self.current_player = (self.current_player + 1) % self.num_players
        # if player fold, next player
        while players[self.current_player].fold:
            self.current_player = (self.current_player + 1) % self.num_players

        # new round task
        if self.current_player < init_player_id:
            self.count += 1
            # 有人錢不夠call的話 全場開牌
            if min([i.fund - (self.bet_option[self.current_bet_level] * (2 if i.check else 1)) for i in
                    players]) < 0 and not self.all_in_num:
                self.all_compare(players)
            # count = 100, 全場開牌
            if self.count >= 100:
                self.all_compare(players)

        return players

    def get_legal_actions(self, players, player_id):
        legal_actions = ['fold']
        if self.all_in_num:
            legal_actions.append('all in')
        else:
            legal_actions.append('call')
            for i in range(self.current_bet_level + 1, 4):
                legal_actions.append(f'raise-{i}')

        if self.count >= 2 and not players[player_id].check:
            legal_actions.append('check')

        if self.count >= 3 and not self.all_in_num:
            legal_actions.append('all in')
            for player in players:
                if player.player_id != player_id and not player.fold:
                    legal_actions.append(f'compare-{player.player_id}')

        return legal_actions

    @staticmethod
    def game_done(players):
        if [i for i in players if not i.fold]:
            return False
        return True

    def all_compare(self, players, all_in_state=False):
        compare_players = [player for player in players if not player.fold]
        if all_in_state:
            live, die = ZhjJudger.judge_winner(compare_players)
            if len(live) > 1:
                players[self.first_all_in_player_id].die()
            for loser in die:
                loser.die()
            final_player = [player for player in players if not player.fold]
            winner_size = len(final_player)
            for winner in final_player:
                winner.fund += self.total_stakes / winner_size
            self.total_stakes = 0
            self.is_over = True
        else:
            if self.all_in_num:
                for player in compare_players[-self.all_in_num:]:
                    stake = player.init_fund - player.fold
                    player.fund += stake
                    self.total_stakes -= stake
                    player.die()
                compare_players = compare_players[:-self.all_in_num]
            live, die = ZhjJudger.judge_winner(compare_players)
            winner_size = len(live)
            for loser in die:
                loser.die()
            for winner in live:
                winner.fund += self.total_stakes / winner_size
            self.total_stakes = 0
            self.is_over = True

    def start_game(self, players):
        in_game_cost = 1
        self.total_stakes += self.num_players * in_game_cost
        for player in players:
            player.fund -= in_game_cost
