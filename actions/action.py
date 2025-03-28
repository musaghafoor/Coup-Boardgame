"""
Defines the action module for Coup. This module contains classes and functions related to player actions. 
"""
from exceptions.game_exceptions import *

class Action:
    """Initialises the parent action class. Contains all the necessary variables needed for actions"""
    def __init__(self, game, player, target=None, coins_needed=0, is_blockable=False, requires_influence=False, action_name='', required_card='', needs_target=False):
        self.game = game
        self.player = player
        self.target = target
        self.coins_needed = coins_needed
        self.is_blockable = is_blockable
        self.requires_influence = requires_influence
        self.action_name = action_name
        self.required_card = required_card
        self.needs_target = needs_target

    def execute(self):
        """Checks if the action can be executed by performing checks. Raises error if it cannot perform the action"""
        if self.player.get_coins() < self.coins_needed:
            raise NotEnoughCoinsError(f"Need at least {self.coins_needed} coins to perform {self.action_name}.")
        if self.target is not None and self.target.is_eliminated:
            raise InvalidTargetError("Selected target is already eliminated!")

    def perform_action(self):
        """Performs the action"""
        raise NotImplementedError(f"{self.action_name} action must implement the perform_action method.")
    
class Income(Action):
    """Income action which makes a player gain 1 coin"""
    def __init__(self, game, player):
        super().__init__(game, player, action_name='Income')

    def perform_action(self):
        super().execute()
        self.player.gain_coins(1)

class ForeignAid(Action):
    """Foreign Aid action which allows a  player to gain 2 coins. Can be blocked by Duke"""
    def __init__(self, game, player):
        super().__init__(game, player, is_blockable=True, action_name='Foreign Aid')
        self.can_block = ["Duke"]

    def perform_action(self):
        super().execute()
        self.player.gain_coins(2)

class Coup(Action):
    """Coup action which requires 7 coins and will eliminate a valid target"""
    def __init__(self, game, player, target):
        super().__init__(game, player, target, coins_needed=7, action_name='Coup', needs_target=True)

    def perform_action(self):
        super().execute()
        self.target.lose_influence()
        self.player.lose_coins(7)

class Tax(Action): #is blockable false
    """Tax action which allows a player to gain 3 coins by claiming Duke"""
    def __init__(self, game, player):
        super().__init__(game, player, requires_influence=True, action_name='Tax', required_card="Duke")

    def perform_action(self):
        super().execute()
        self.player.gain_coins(3)

class Assassinate(Action):
    """Assassinate action which allows a player to assassinate a valid target, paying a fee of 3 coins. It can be blocked by Contessa"""
    def __init__(self, game, player, target):
        super().__init__(game, player, target, coins_needed=3, requires_influence=True, is_blockable=True, action_name='Assassinate', required_card='Assassin', needs_target=True)
        self.can_block = ["Contessa"]

    def perform_action(self):
        super().execute()
        self.target.lose_influence()
        self.player.lose_coins(3)

class Steal(Action):
    """Steal action which allows a player to steal 2 coins from a valid target. Can be blocked by Captain or Ambassador"""
    def __init__(self, game, player, target):
        super().__init__(game, player, target, is_blockable=True, requires_influence=True, action_name='Steal', required_card="Captain", needs_target=True)
        self.can_block = ["Captain", "Ambassador"]

    def perform_action(self):
        super().execute()

        target_coins = self.target.get_coins()
        if target_coins == 0:
            raise InsufficientCoinsToStealError("Target has no coins to steal from.")

        if target_coins >= 2:
            stolen_coins = 2
        else:  
            stolen_coins = target_coins 

        self.target.lose_coins(stolen_coins)
        self.player.gain_coins(stolen_coins)


class Exchange(Action):
    """Exchange action which allows a player to draw upto 2 cards from the deck and return upto 2 cards back to the deck."""
    def __init__(self, game, player):
        super().__init__(game, player, requires_influence=True, action_name='Exchange', required_card="Ambassador")

    def perform_action(self):
        if len(self.game.deck.cards) < 1:
            raise DeckEmptyException("Not enough cards in the deck to perform an exchange.")

        if len(self.game.deck.cards) == 1:
            drawn_cards = [self.game.deck.draw_card()]
        else:
            drawn_cards = [self.game.deck.draw_card(), self.game.deck.draw_card()]
        returned_cards = self.player.select_exchange_cards(drawn_cards)

        for card in returned_cards:
            self.game.deck.return_card(card)

class Contessa(Action): #is blockable false
    """Contessa action which allows the  player to block the Assassin"""
    def __init__(self, game, player):
        super().__init__(game, player, requires_influence=True, action_name='Contessa', required_card="Contessa")

    def perform_action(self):
        super().execute()