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

    def verify(self):
        if self.player.get_coins() < self.coins_needed:
            raise NotEnoughCoinsError(f"Need at least {self.coins_needed} coins to perform {self.action_name}.")
        if self.target is not None and self.target.is_eliminated:
            raise InvalidTargetError("Selected target is already eliminated!")

    def perform_action(self):
        self.verify()
        self.execute()

    def execute(self):
        raise NotImplementedError(f"{self.action_name} action must implement the execute method.")

class Income(Action):
    def execute(self):
        self.player.gain_coins(1)

class ForeignAid(Action):
    def execute(self):
        self.player.gain_coins(2)

class Coup(Action):
    def execute(self):
        self.target.lose_influence()
        self.player.lose_coins(7)

class Tax(Action):
    def execute(self):
        self.player.gain_coins(3)

class Assassinate(Action):
    def execute(self):
        self.target.lose_influence()
        self.player.lose_coins(3)

class Steal(Action):
    def execute(self):
        target_coins = self.target.get_coins()
        stolen_coins = min(2, target_coins)
        self.target.lose_coins(stolen_coins)
        self.player.gain_coins(stolen_coins)

class Exchange(Action):
    def execute(self):
        if len(self.game.deck.cards) < 2:
            raise DeckEmptyException("Not enough cards in the deck to perform an exchange.")

        drawn_cards = [self.game.deck.draw_card() for _ in range(2)]
        returned_cards = self.player.select_exchange_cards(drawn_cards)
        for card in returned_cards:
            self.game.deck.return_card(card)
