import random
from rlcard.games.holdem.utils import init_deck
from rlcard.games.holdem.card import holdemCard, computer_power
compute = computer_power

class holdemDealer(object):
    def __init__(self):
        self.deck = init_deck()
        self.shuffle()
        self.community = []

    def shuffle(self):
        random.shuffle(self.deck)
    def deal_cards(self, player, num):
        """ Deal some cards from deck to one player

        Args:
            player (holdemPlayer): The object of ZhjPlayer
            num (int): The number of cards to be dealed
        """
        for _ in range(num):
            player.hand.append(self.deck.pop()) 
        #player.power = ZhjCard.compute_power(player.hand)            
    def deal_community(self):
        for _ in range(5):
            self.community.append(self.deck.pop())
        return self.community
    @staticmethod
    def computer_power(player, community):
        player.power = compute.eval_hand(player.hand, community)
        
# =============================================================================
# compute win rate def 
# =============================================================================
def estimate_hole_card_win_rate(nb_simulation, nb_player, \
                                hole_card, community_card=None):
    if not community_card: community_card = []
    win_count = sum([montecarlo_simulation(nb_player, hole_card, \
                community_card) for _ in range(nb_simulation)])
    return 1.0 * win_count / nb_simulation       
        
def montecarlo_simulation(nb_player, hole_card, community_card):
    community_card = fill_community_card(community_card, \
                                         used_card=hole_card+community_card)
    unused_cards = pick_unused_card((nb_player-1)*2, \
                                    hole_card + community_card)
    opponents_hole = [unused_cards[2*i:2*i+2] for i in range(nb_player-1)]
    opponents_score = [compute.eval_hand(hole, community_card)\
                       for hole in opponents_hole]
    my_score = compute.eval_hand(hole_card, community_card)
    return 1 if my_score >= max(opponents_score) else 0

def fill_community_card(base_cards, used_card):
    need_num = 5 - len(base_cards)
    return base_cards + pick_unused_card(need_num, used_card)

def pick_unused_card(card_num, used_card):
    used = [card.to_id() for card in used_card]
    unused = [card_id for card_id in range(1, 53) if card_id not in used]
    choiced = random.sample(unused, card_num)
    return [holdemCard.from_id(card_id) for card_id in choiced]