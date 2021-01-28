import numpy as np
class holdemJudger(object):

    @staticmethod
    def judge_winner(compare_players):
        """ Judge the winner of the game

        Args:
            compare_players (list): list of holdemPlayer

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
    @staticmethod
    def compare_winner(players):
        compare_players = [player for player in players if not player.fold]
        if len(compare_players) != 1:
            live, die = holdemJudger.judge_winner(compare_players)
        else:
            live = compare_players
        return live
    
    @staticmethod
    def split_pot(players, total_stakes):
        all_in_players = [player.player_id for player in players if player.all_in]
        stacks = np.asarray(total_stakes)
        all_in_stacks = np.unique(stacks[all_in_players]).tolist()
        pot = []
        be_stack = 0
        if all_in_stacks:
            for stack in all_in_stacks:
                diff_stack = (stack - be_stack)
                stacks = stacks - (stack - be_stack)
                eligibles = [players[i] for i in range(len(stacks)) if stacks[i] >= 0 and not players[i].fold]
                amount = diff_stack*np.sum(stacks >= 0) + np.sum(stacks[stacks < 0]+diff_stack)
                stacks[stacks < 0] = 0
                be_stack = stack
                pot.append({'amount':amount, 'eligibles':eligibles})
        if max(stacks) > 0:
            eligibles = [players[i] for i in range(len(stacks)) if (stacks-max(stacks))[i] >= 0 and not players[i].fold]
            if not eligibles:
                eligibles = [players[i] for i in range(len(stacks)) if not players[i].fold]
            pot.append({'amount':sum(stacks), 'eligibles':eligibles})
        return pot
