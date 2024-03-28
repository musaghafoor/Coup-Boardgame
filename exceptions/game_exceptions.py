"""
This module defines the exceptions for the game. It is responsible for handling the exceptions that are raised in the game.
"""

class GameException(Exception):
    """
    This class is the base class for all the exceptions in the game.
    """
    def __init__(self, message="A game exception occurred."):
        super().__init__(message)

class NoCardsLeftInDeck(GameException):
    """
    Exception raised when there are no cards left in the deck.
    """
    def __init__(self, message="There are no cards left in the deck!"):
        super().__init__(message)

