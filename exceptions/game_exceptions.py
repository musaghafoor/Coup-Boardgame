"""
This module defines the exceptions for the game. It is responsible for handling the exceptions that are raised in the game.
"""
#https://stackoverflow.com/questions/2146618/raising-an-exception-vs-printing#:~:text=Raising%20an%20error%20halts%20the,output%20may%20never%20be%20seen.

class GameException(Exception):
    """
    Base class for all game-specific exceptions to allow for targeted exception handling related to game logic.
    """
    pass

class NoCardsLeftInDeck(GameException):
    """
    Exception raised when there are no cards left in the deck to be drawn.
    """
    def __init__(self, message="Attempted to draw a card from an empty deck."):
        super().__init__(message)

class NotEnoughCoinsError(GameException):
    """
    Exception raised when the player attempts an action that requires more coins than they have.
    """
    def __init__(self, coins_needed, message=None):
        if message is None:
            message = f"Not enough coins to perform this action. You need at least {coins_needed} coins."
        super().__init__(message)

class TargetNeeded(GameException):
    """
    Exception raised when a targeted action is attempted without specifying a target.
    """
    def __init__(self, message="This action requires a target to be specified."):
        super().__init__(message)

class InvalidTargetError(GameException):
    """
    Exception raised when an action is attempted on an invalid target, such as a non-existent player or an eliminated player.
    """
    def __init__(self, message="The selected target is invalid, possibly eliminated or not in the game."):
        super().__init__(message)

class DeckEmptyException(GameException):
    """
    Exception raised when a deck operation is attempted but the deck is empty.
    """
    def __init__(self, message="Cannot perform the operation: The deck is empty."):
        super().__init__(message)

class PlayerEliminated(GameException):
    """
    Exception raised when an action is attempted involving an eliminated player.
    """
    def __init__(self, message="The player is already eliminated and cannot perform actions."):
        super().__init__(message)

class HandIsFull(GameException):
    """
    Exception raised when a player tries to draw or receive a card but their hand is already full.
    """
    def __init__(self, message="Cannot add more cards: The player's hand is already full."):
        super().__init__(message)

class NotImplemented(GameException):
    """
    Exception typically raised to indicate an abstract method or functionality that hasn't been implemented yet.
    """
    def __init__(self, feature_name, message=None):
        if message is None:
            message = f"The feature '{feature_name}' is not implemented yet."
        super().__init__(message)

class InsufficientTreasuryCoinsError(GameException):
    def __init__(self, message="Not enough coins in the treasury to perform this action."):
        super().__init__(message)

class TooManyCoinsError(GameException):
    def __init__(self, message="Player cannot have more coins than the maximum limit."):
        super().__init__(message)

class InsufficientCoinsToStealError(GameException):
    def __init__(self, message="The target player does not have enough coins to steal."):
        super().__init__(message)

class PlayerEliminatedError(GameException):
    """
    Exception raised when an operation is attempted on an eliminated player.
    """
    def __init__(self, message="This player is already eliminated and cannot perform any actions."):
        super().__init__(message)

class HandIsFullError(GameException):
    """
    Exception raised when a player attempts to take a card with a full hand.
    """
    def __init__(self, message="The player's hand is full and cannot hold any more cards."):
        super().__init__(message)