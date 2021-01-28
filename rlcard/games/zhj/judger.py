class ZhjJudger(object):

    @staticmethod
    def judge_winner(compare_players):
        """ Judge the winner of the game

        Args:
            compare_players (list): list of ZhjPlayer

        Returns:
            (list): The player id of the winner
        """
        if len(compare_players) == 2:
            if compare_players[0].power > compare_players[1].power:
                return [compare_players[0]], [compare_players[1]]
            return [compare_players[1]], [compare_players[0]]
        else:
            max_power = max([i.power for i in compare_players])
            live, die = [], []
            for player in compare_players:
                if player.power == max_power:
                    live.append(player)
                else:
                    die.append(player)
            return live, die
