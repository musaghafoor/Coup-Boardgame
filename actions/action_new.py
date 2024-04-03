from exceptions.game_exceptions import *

class Action:
    def __init__(self, game, player, target=None, coins_needed=0, is_blockable=False, requires_influence=False, action_name='', required_card=''):
        self.game = game
        self.player = player
        self.target = target
        self.coins_needed = coins_needed
        self.is_blockable = is_blockable
        self.requires_influence = requires_influence
        self.action_name = action_name
        self.required_card = required_card

    def execute(self):
        if self.player.get_coins() < self.coins_needed:
            raise NotEnoughCoinsError(f"Need at least {self.coins_needed} coins to perform {self.action_name}.")
        if self.target is not None and self.target.is_eliminated:
            raise InvalidTargetError("Selected target is already eliminated!")

    def perform_action(self):
        raise NotImplementedError(f"{self.action_name} action must implement the perform_action method.")

class Income(Action):
    def __init__(self, game, player):
        super().__init__(game, player, action_name='Income')

    def perform_action(self):
        super().execute()
        self.player.gain_coins(1)

class ForeignAid(Action):
    def __init__(self, game, player):
        super().__init__(game, player, is_blockable=True, action_name='Foreign Aid')
        self.can_block = ["Duke"]

    def perform_action(self):
        super().execute()
        self.player.gain_coins(2)

class Coup(Action):
    def __init__(self, game, player, target):
        super().__init__(game, player, target, coins_needed=7, action_name='Coup')

    def perform_action(self):
        super().execute()
        self.target.lose_influence()
        self.player.lose_coins(7)

class Tax(Action): #is blockable false
    def __init__(self, game, player):
        super().__init__(game, player, requires_influence=True, action_name='Tax', required_card="Duke")

    def perform_action(self):
        super().execute()
        self.player.gain_coins(3)

class Assassinate(Action):
    def __init__(self, game, player, target):
        super().__init__(game, player, target, coins_needed=3, is_blockable=True, action_name='Assassinate', required_card='Assassin')
        self.can_block = ["Contessa"]

    def perform_action(self):
        super().execute()
        self.target.lose_influence()
        self.player.lose_coins(3)

class Steal(Action):
    def __init__(self, game, player, target):
        super().__init__(game, player, target, is_blockable=True, requires_influence=True, action_name='Steal', required_card="Captain")
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
    def __init__(self, game, player):
        super().__init__(game, player, requires_influence=True, action_name='Exchange', required_card="Ambassador")

    def perform_action(self):
        if len(self.game.deck.cards) < 2:
            raise DeckEmptyException("Not enough cards in the deck to perform an exchange.")

        drawn_cards = [self.game.deck.draw_card(), self.game.deck.draw_card()]
        returned_cards = self.player.select_exchange_cards(drawn_cards)

        for card in returned_cards:
            self.game.deck.return_card(card)
