from game.game_new import Game
from game.player_new import Player
from cards.deck import Deck

def setup_game():
    # Create deck
    deck = Deck()

    # Initialize the game
    game = Game(deck)

    # List of example player names
    player_names = ["Alice", "Bob", "Charlie", "David"]

    # Create players and assign them to the game
    for name in player_names:
        player = Player(name)
        game.players.append(player)

    # Now that all players are added to the game, call the setup method
    game.setup()

    return game

def main():
    game = setup_game()

    # Start the game loop
    game.play_game()

if __name__ == "__main__":
    main()
