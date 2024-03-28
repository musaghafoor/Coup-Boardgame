"""
This module defines the Deck class. It is responsible for shuffling and dealing out cards to the players.
"""

import random
from cards.card import Card
from exceptions.game_exceptions import GameException, NoCardsLeftInDeck

class Deck:
    def __init__(self):
        """Define the characters and the number of each card to be included in the deck"""
        self.cards = [] # Initialise the cards list
        characters = ["Duke", "Assassin", "Captain", "Ambassador", "Contessa"]
        number_of_each_character = 3
        
        # Create the deck by looping through each character a number of times
        for character in characters:
            for i in range(number_of_each_character):
                self.cards.append(Card(character))
        
        self.shuffle()

    def shuffle(self):
        """Shuffles the cards in the deck"""
        random.shuffle(self.cards)

    def draw_card(self):
        """Draws a card from the top of the deck"""
        if not self.cards:
            raise NoCardsLeftInDeck("There are no cards left in the deck!")
        return self.cards.pop()
