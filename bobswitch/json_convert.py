
def convert_card(card):
    return { "suit": int(card.suit), "rank": int(card.rank) }

def convert_hand(hand):
    return [convert_card(card) for card in hand.cards]

def convert_state_start(number_of_players, hand):
    return {
        "number_of_players": number_of_players,
        "hand": convert_hand(hand)
    }

