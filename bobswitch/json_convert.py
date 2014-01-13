
def convert_card(card):
    return { "suit": int(card.suit), "rank": int(card.rank) }

def convert_hand(hand):
    return [convert_card(card) for card in hand.cards]

def convert_state_start(players, starting_player, top_card, hand):
    players = [player.name for player in players]

    return {
        "players": players,
        "starting_player": starting_player,
        "number_of_players": len(players),
        "hand": convert_hand(hand),
        "top_card": convert_card(top_card)
    }

def convert_play_response(play_response):
    return {
        "success": play_response.success,
        "message": play_response.message
    }
    
