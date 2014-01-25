
def convert_card(card):
    return { "suit": int(card.suit), "rank": int(card.rank) }

def convert_hand(hand):
    return [convert_card(card) for card in hand.cards]

def convert_state(state):
    state_int = int(state)

    if state_int == 0:
        return "normal"
    elif state_int == 1:
        return "pick"
    elif state_int == 2:
        return "wait"
    else:
        return "finished"

def convert_state_start(state, players, player_hands, starting_player, top_card, hand):
    players = [{ 
        "name": player.name, 
        "count": player_hands[player.name].hand.number_of_cards()
        } for player in players]

    return {
        "players": players,
        "starting_player": starting_player,
        "number_of_players": len(players),
        "hand": convert_hand(hand),
        "top_card": convert_card(top_card),
        "state": convert_state(state)
    }

def convert_play_response(play_response):
    return {
        "success": play_response.success,
        "message": play_response.message
    }
    
