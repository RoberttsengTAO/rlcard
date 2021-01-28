import random

from rlcard.games.zhj.utils import init_deck
from rlcard.games.zhj.card import ZhjCard


class ZhjDealer(object):
    def __init__(self):
        self.deck = init_deck()
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.deck)

    def deal_cards(self, player, num):
        """ Deal some cards from deck to one player

        Args:
            player (ZhjPlayer): The object of ZhjPlayer
            num (int): The number of cards to be dealed
        """
        for _ in range(num):
            player.hand.append(self.deck.pop())

        player.power = ZhjCard.compute_power(player.hand)
