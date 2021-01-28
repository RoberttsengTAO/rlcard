from numpy.random import randint
class holdemPlayer(object):
    def __init__(self, player_id: int, fund: float, small_blind_amount: float):
        """ Initilize a player.

        Args:
            player_id (int): The id of the player
            fund (float): The funds
        """
        #fund = int(randint(small_blind_amount*2, fund, 1))
        self.player_id = player_id
        self.hand = []
        self.bet_cost = 0
        self.fund = 20000
        self.init_fund = 20000
        self.fold = False
        self.check = False
        self.power = 0
        self.all_in = False
        self.win_rate = [0]*4
        self.raise_count = 0
        self.check_count = 0

    def die(self):
        self.check = False
        self.fold = True
    def bet_reset(self):
        self.bet_cost = 0
    def reset(self):
        self.check = False
    def all_reset(self):
        self.check = False
        self.bet_cost = 0

    @staticmethod
    def get_fold(player):
        if isinstance(player, holdemPlayer):
            return player.fold

    @staticmethod
    def get_live(player):
        if isinstance(player, holdemPlayer):
            return not player.fold


if __name__ == '__main__':
    player_A = holdemPlayer(0, 100.0, 1)
    print(player_A.player_id)
    print(player_A.hand)
    print(player_A.fund)
    print(holdemPlayer.get_live(player_A))
