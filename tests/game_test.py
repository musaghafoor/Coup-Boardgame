import unittest
from cards.deck import Deck
from game.player_new import Player
from cards.card import Card
from game.game_new import Game
from actions.action_new import Action
from exceptions.game_exceptions import *

class GameTest(unittest.TestCase):
    def setUp(self):
        """Initialize game with a deck and players for each test."""
        self.deck = Deck()
        self.game = Game(self.deck)
        self.player1 = Player("Player 1")
        self.player2 = Player("Player 2")
        self.game.players = [self.player1, self.player2]
        self.card1 = Card("Duke")
        self.card2 = Card("Assassin")
        self.card3 = Card("Captain")
        self.card4 = Card("Ambassador")
        self.card5 = Card("Contessa")

    def test_game_initialization(self):
        """Test that the game initializes with players and a shuffled deck."""
        self.assertEqual(len(self.game.players), 2)
        self.assertIsInstance(self.game.deck, Deck)
        self.assertFalse(self.game.deck.cards == sorted(self.game.deck.cards, key=lambda x: x.name))

    def test_setup_game(self):
        """Test setting up the game deals two cards to each player and sets coins."""
        self.game.setup()
        for player in self.game.players:
            self.assertEqual(len(player.hand), 2)
            self.assertEqual(player.coins, 2)

    def test_play_turn(self):
        """Test playing a turn advances the game correctly."""
        self.game.setup()
        current_player = self.game.players[self.game.current_player_index]
        self.game.play_turn(current_player)
        # Ensure turn advances to next player
        self.assertNotEqual(current_player, self.game.players[self.game.current_player_index])

    def test_execute_action(self):
        """Test executing actions affects the game state appropriately."""
        self.game.setup()
        # Test an action like Income or Coup
        # Actions should be tested individually for each type

    def test_end_game_conditions(self):
        """Test game correctly identifies the end game and determines the winner."""
        self.game.setup()
        # Manually set the game state to an end game condition
        # Test if the game correctly identifies the winner
        
    def test_foreign_aid_block(self):
        """Test that Foreign Aid can be blocked and handle challenges."""
        self.game.setup()
        self.player1.add_card(self.card1)  # Duke card for blocking
        # Assume player2 tries to take foreign aid which player1 blocks
        foreign_aid_action = ForeignAid(self.game, self.player2)
        self.game.execute_action(foreign_aid_action)
        # Here you should test the logic of blocking and possibly challenging the block

    def test_coup_action(self):
        """Test executing a Coup reduces coins and removes influence from the target."""
        self.game.setup()
        self.player1.coins = 7  # Set coins for coup
        target = self.player2
        coup_action = Coup(self.game, self.player1, target)
        coup_action.perform_action()
        self.assertEqual(self.player1.coins, 0)
        self.assertTrue(target.is_eliminated or len(target.hand) < 2)

    def test_assassinate_action(self):
        """Test Assassinate action and its interaction with Contessa block."""
        self.game.setup()
        self.player1.coins = 3  # Set coins for assassination
        self.player2.add_card(self.card5)  # Contessa card for blocking assassination
        assassinate_action = Assassinate(self.game, self.player1, self.player2)
        assassinate_action.perform_action()
        # Test the assassination logic and potential Contessa block here

    def test_exchange_action(self):
        """Test Exchange action allows swapping cards with the deck."""
        self.game.setup()
        exchange_action = Exchange(self.game, self.player1)
        initial_hand_count = len(self.player1.hand)
        exchange_action.perform_action()
        self.assertEqual(len(self.player1.hand), initial_hand_count)  # Assuming exchange completed successfully

    def test_end_game_winner(self):
        """Test game correctly identifies the winner."""
        self.game.setup()
        # Eliminate all but one player to simulate end game
        for player in self.game.players[:-1]:
            player.set_eliminated(True)
        self.assertTrue(self.game.is_game_over())
        self.assertEqual(self.game.players_remaining()[0], self.game.players[-1])

if __name__ == "__main__":
    unittest.main()
