# test_deck.py
import unittest
from cards.deck import Deck
from cards.card import Card
from exceptions.game_exceptions import *
class DeckTest(unittest.TestCase):
    def setUp(self):
        """Initialize a new deck for each test."""
        self.deck = Deck()

    def test_deck_initialization(self):
        """Test that the deck is initialized with the correct number of cards and is shuffled."""
        self.assertEqual(len(self.deck.cards), 15)  # 5 characters * 3 cards each
        # Test for shuffled deck can be tricky since we can't predict randomness, but we can check types
        self.assertTrue(all(isinstance(card, Card) for card in self.deck.cards))

    def test_draw_card(self):
        """Test that drawing a card reduces the deck size and returns a card."""
        initial_count = len(self.deck.cards)
        card = self.deck.draw_card()
        self.assertIsInstance(card, Card)
        self.assertEqual(len(self.deck.cards), initial_count - 1)

    def test_return_card(self):
        """Test returning a card to the deck."""
        card = self.deck.draw_card()  # Draw a card first
        self.deck.return_card(card)   # Then return it
        self.assertIn(card, self.deck.cards)  # Check if the card is in the deck

    def test_no_cards_left_exception(self):
        """Test that NoCardsLeftInDeck is raised when drawing from an empty deck."""
        while self.deck.cards:  # Empty the deck
            self.deck.draw_card()
        with self.assertRaises(NoCardsLeftInDeck):
            self.deck.draw_card()

if __name__ == "__main__":
    unittest.main()
