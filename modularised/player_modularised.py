from exceptions.game_exceptions import *

class Player:
    def __init__(self, name, ui):
        self.name = name
        self.game = None
        self.ui = ui
        self.reset()


    def set_game(self, game):
        self.game = game

    def reset(self):
        self.hand = []
        self.coins = 2
        self._is_eliminated = False
        self.influences_lost = []

    def add_card(self, card):
        if self._is_eliminated:
            raise PlayerEliminatedError("Cannot add card to hand as player is eliminated!")
        if not card:
            raise GameException("Cannot add a null card to hand!")
        if len(self.hand) >= 2:
            raise HandIsFullError("Player cannot have more than 2 cards!")

        self.hand.append(card)

    def lose_coins(self, amount):
        if amount > self.coins:
            raise NotEnoughCoinsError(f"{self.name} cannot lose more coins than they have.")
        self.coins -= amount

    def gain_coins(self, amount):
        self.coins += amount

    def get_coins(self):
        return self.coins

    @property
    def is_eliminated(self):
        return self._is_eliminated

    def set_eliminated(self, eliminated):
        if not isinstance(eliminated, bool):
            raise GameException("Eliminated status must be a boolean value!")
        self._is_eliminated = eliminated
        if eliminated:
            self.ui.display_message(f"{self.name} is eliminated!")

    def lose_influence(self):
        if self.is_eliminated:
            raise PlayerEliminatedError("Cannot lose influence as player is eliminated!")
        if not self.hand:
            raise GameException("Cannot lose influence as player has no cards!")

        if len(self.hand) == 1:
            self.lose_card(0)
        else:
            card_index = self.ui.prompt_for_card_loss(self.hand, self.name)
            self.lose_card(card_index)

    def lose_card(self, card_index):
        if card_index < 0 or card_index >= len(self.hand):
            raise GameException("Invalid card index for losing influence!")
        
        lost_card = self.hand.pop(card_index)
        self.influences_lost.append(lost_card)
        self.ui.display_message(f"{self.name} has lost their {lost_card} influence.")
        if not self.hand:
            self.set_eliminated(True)

    def has_card(self, card_name):
        return any(card.name == card_name for card in self.hand)

    def get_card_index(self, card_name):
        for index, card in enumerate(self.hand):
            if card.name == card_name:
                return index
        return None

    def swap_card(self, card_index):
        if self.game is None:
            raise GameException("Player is not associated with a game.")

        removed_card = self.hand.pop(card_index)
        new_card = self.game.deck.draw_card()
        self.hand.append(new_card)
        self.game.deck.return_card(removed_card)
        self.ui.display_message(f"{self.name} swapped a {removed_card} for a new card.")

    def choose_action(self):
        actions = self.game.available_actions(self)  # Assuming this method is implemented in Game
        return self.ui.prompt_for_action(actions)

    def choose_target(self, targets):
        # Utilize the UI instance for choosing the target
        return self.ui.prompt_for_target(targets)

    def __str__(self):
        return self.name
