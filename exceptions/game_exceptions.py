"""
This module defines the exceptions for the game. It is responsible for handling the exceptions that are raised in the game.
"""
#https://stackoverflow.com/questions/2146618/raising-an-exception-vs-printing#:~:text=Raising%20an%20error%20halts%20the,output%20may%20never%20be%20seen.

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

class NotEnoughCoins(GameException):
    """
    Exception raised when the player has insufficient coins.
    """

    def __init__(self, coins_needed, message="You do not have enough coins!"):
        super().__init__(message)
        self.coins_needed = coins_needed

class TargetNeeded(GameException):
    """
    Exception raised when a target is needed for the action.
    """
    def __init__(self, message="A target is needed for this action!"):
        super().__init__(message)

class InvalidTarget(GameException):
    """
    Exception raised when the target is invalid.
    """
    def __init__(self, message="Invalid target!"):
        super().__init__(message)

class DeckEmptyException(GameException):
    """
    Exception raised when the deck is empty.
    """
    def __init__(self, message="The deck is empty!"):
        super().__init__(message)

class PlayerEliminated(GameException):
    """
    Exception raised when a player is eliminated.
    """
    def __init__(self, message="Player eliminated!"):
        super().__init__(message)

class HandIsFull(GameException):
    """
    Exception raised when the players hand is full.
    """
    def __init__(self, message="The players hand is full!"):
        super().__init__(message)

class NotImplemented(GameException):
    """
    Exception raised when a method is not implemented.
    """
    def __init__(self, message="Method not implemented!"):
        super().__init__(message)