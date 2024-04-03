"""
This module defines the Deck class. It is responsible for shuffling and dealing out cards to the players.
"""

import random
from cards.card import Card
from exceptions.game_exceptions import GameException, NoCardsLeftInDeck

class Deck:
    def __init__(self):
        """Initializes a new deck of cards."""
        self.cards = []  # Starts with an empty list of cards
        self.set_up_deck()

    def set_up_deck(self):
        """Fills the deck with the standard set of cards."""
        characters = ["Duke", "Assassin", "Captain", "Ambassador", "Contessa"]
        number_of_each_character = 3
        for character in characters:
            for _ in range(number_of_each_character):
                self.cards.append(Card(character))
        self.shuffle()  # Shuffles the deck after initialization

    def shuffle(self):
        """Shuffles the deck using a more secure random number generator."""
        random.SystemRandom().shuffle(self.cards)

    def draw_card(self):
        """Removes and returns the top card of the deck. Raises an exception if the deck is empty."""
        if self.cards:
            return self.cards.pop()
        else:
            raise NoCardsLeftInDeck("There are no more cards left to draw from the deck.")

    def return_card(self, card):
        """Returns a card to the deck and shuffles it back in."""
        if card not in self.cards:
            self.cards.append(card)
            self.shuffle()
        else:
            raise GameException(f"The card {card} is already in the deck.")