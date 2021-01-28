class ZhjCard(object):
    info = {
        'suit': ['S', 'H', 'D', 'C'],
        'number': ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
    }
    rank_dict = dict(zip(info['number'], list(range(len(info['number'])))))

    def __init__(self, suit, number):
        """ Initialize the class of Card

        Args:
            suit (str): The suit of card
            number (str): The number of card
        """
        self.suit = suit
        self.number = number
        self.rank = self.rank_dict[number]
        self.str = self.__str__()

    def __str__(self):
        """ Get the string representation of card

        Return:
            (str): The string of card's suit and rank
        """
        return self.suit + '-' + self.number

    @staticmethod
    def compute_power(hand):
        """
        :param hand: list[ZhjCard]
        :return: power: int
        """
        # avg. power: K98 -> 110706/ (10**6)
        number = [i.rank for i in hand]
        suit = [i.suit for i in hand]

        number = sorted(number)
        if number[0] == number[1] and number[1] != number[2]:
            number = [number[2], number[1], number[1]]

        same_suit = suit[0] == suit[1] == suit[2]
        is_pair = number[1] == number[2]
        is_seq = (number[0] == number[1] - 1 == number[2] - 2) or (number == [0, 1, 12])
        is_three = number[0] == number[1]

        power = number[0] + number[1] * 10 ** 2 + number[2] * 10 ** 4
        if is_three:
            power += 5 * 10 ** 6
        if is_seq:
            power += 2 * 10 ** 6
        if same_suit:
            power += 3 * 10 ** 6
        if is_pair:
            power += 10 ** 6

        return power / (10**6)
