from cards.deck import Deck
from modularised.player_modularised import Player
from modularised.game_modularised import Game
from game.game_ui import GameUI

def main():
    # Initialize game components
    ui = GameUI()
    deck = Deck()
    player_names = ["Alice", "Bob", "Charlie", "Dana"]  # Example player names

    # Create player objects
    players = [Player(name, ui) for name in player_names]

    # Initialize the game
    game = Game(players, deck, ui)

    # Set up the game
    game.setup()

    # Start the game
    game.play_game()

if __name__ == "__main__":
    main()
