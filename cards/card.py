"""
This module defines the Card class. Each card has a name attribute which can be used to identify the card
"""

class Card:
    """Represents a card in the game"""
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name #Allows us to print the card, making it easier to debug in the future