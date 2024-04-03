# test_player.py
import unittest
from cards.deck import Deck
from game.player_new import Player
from cards.card import Card
from game.game_new import Game
from exceptions.game_exceptions import *

class PlayerTest(unittest.TestCase):
    def setUp(self):
        """Initialize a new player and cards for each test."""
        deck = Deck()
        game = Game(deck)
        self.player = Player("Test Player")  # Associate each player with the game
        game.players.append(self.player)
        self.card1 = Card("Duke")
        self.card2 = Card("Assassin")
        self.card3 = Card("Captain")

    def test_player_initialization(self):
        """Test player is initialized with correct attributes."""
        self.assertEqual(self.player.name, "Test Player")
        self.assertEqual(self.player.coins, 2)
        self.assertFalse(self.player.is_eliminated)
        self.assertEqual(len(self.player.hand), 0)

    def test_reset(self):
        """Test resetting the player's state."""
        self.player.add_card(self.card1)
        self.player.add_card(self.card2)
        self.player.lose_coins(1)
        self.player.reset()

        self.assertEqual(len(self.player.hand), 0)
        self.assertEqual(self.player.coins, 2)
        self.assertFalse(self.player.is_eliminated)

    def test_add_card(self):
        """Test adding cards to the player's hand."""
        self.player.add_card(self.card1)
        self.assertIn(self.card1, self.player.hand)
        self.player.add_card(self.card2)
        self.assertIn(self.card2, self.player.hand)

        with self.assertRaises(HandIsFullError):
            self.player.add_card(self.card3)

    def test_lose_coins(self):
        """Test losing coins and handling insufficient coins."""
        self.player.lose_coins(1)
        self.assertEqual(self.player.coins, 1)

        with self.assertRaises(NotEnoughCoinsError):
            self.player.lose_coins(2)

    def test_gain_coins(self):
        """Test gaining coins."""
        self.player.gain_coins(3)
        self.assertEqual(self.player.coins, 5)

    def test_lose_influence(self):
        """Test losing influence and player elimination."""
        self.player.add_card(self.card1)
        self.player.add_card(self.card2)

        self.player.lose_influence()  # Assume this removes the first card
        self.assertEqual(len(self.player.hand), 1)
        self.assertFalse(self.player.is_eliminated)

        self.player.lose_influence()
        self.assertTrue(self.player.is_eliminated)

    def test_has_card(self):
        """Test checking if player has a specific card."""
        self.player.add_card(self.card1)
        self.assertTrue(self.player.has_card("Duke"))
        self.assertFalse(self.player.has_card("Assassin"))

    def test_set_eliminated(self):
        """Test setting player's elimination status."""
        self.assertFalse(self.player.is_eliminated)
        self.player.set_eliminated(True)
        self.assertTrue(self.player.is_eliminated)

        with self.assertRaises(GameException):
            self.player.set_eliminated("not a boolean")

    def test_lose_card(self):
        """Test losing a card from the player's hand."""
        self.player.add_card(self.card1)
        self.player.add_card(self.card2)
        self.player.lose_card(0)
        self.assertNotIn(self.card1, self.player.hand)
        self.assertIn(self.card2, self.player.hand)

        # Test losing the last card results in elimination
        self.player.lose_card(0)
        self.assertTrue(self.player.is_eliminated)

    def test_lose_card_with_invalid_index(self):
        """Test losing a card with invalid index raises an exception."""
        self.player.add_card(self.card1)
        with self.assertRaises(GameException):
            self.player.lose_card(5)  # Invalid index

    def test_return_card_to_full_hand(self):
        """Test returning a card to a full hand raises an exception."""
        self.player.add_card(self.card1)
        self.player.add_card(self.card2)
        with self.assertRaises(HandIsFullError):
            self.player.add_card(self.card3)

    def test_add_card_to_eliminated_player(self):
        """Test adding a card to an eliminated player raises an exception."""
        self.player.set_eliminated(True)
        with self.assertRaises(PlayerEliminatedError):
            self.player.add_card(self.card1)

    def test_swap_card(self):
        """Test swapping a card in the player's hand."""
        self.player.add_card(self.card1)
        original_hand = list(self.player.hand)
        
        with self.assertRaises(GameException):
            self.player.swap_card(0)  # Invalid index for swap should raise GameException

    def test_invalid_swap_card(self):
        """Test invalid swap card index raises an exception."""
        self.player.add_card(self.card1)
        with self.assertRaises(GameException):
            self.player.swap_card(5)  # Invalid index for swap

    def test_prompt_show_card(self):
        """Test prompt show card logic, simulating user input."""
        self.player.add_card(self.card1)
        # Simulating user input would require patching input or restructuring code for better testability
        # For now, consider how you might test interactive methods or refactor them for easier testing


if __name__ == "__main__":
    unittest.main()
