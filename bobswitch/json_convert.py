
def convert_card(card):
    return { "suit": int(card.suit), "rank": int(card.rank) }

def convert_hand(hand):
    return [convert_card(card) for card in hand.cards]

