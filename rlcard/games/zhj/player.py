class ZhjPlayer(object):
    def __init__(self, player_id: int, fund: float):
        """ Initilize a player.

        Args:
            player_id (int): The id of the player
            fund (float): The funds
        """
        self.player_id = player_id
        self.hand = []
        self.fund = fund
        self.init_fund = fund
        self.fold = False
        self.check = False
        self.power = 0

    def die(self):
        # self.fund = 0
        self.check = False
        self.fold = True

    @staticmethod
    def get_fold(player):
        if isinstance(player, ZhjPlayer):
            return player.fold

    @staticmethod
    def get_live(player):
        if isinstance(player, ZhjPlayer):
            return not player.fold


if __name__ == '__main__':
    player_A = ZhjPlayer(0, 100.0)
    print(player_A.player_id)
    print(player_A.hand)
    print(player_A.fund)
    print(ZhjPlayer.get_live(player_A))
