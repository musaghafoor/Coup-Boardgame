"""
Defines the action module for Coup. This module contains classes and functions related to player actions. 
"""
#GO THROUGH THE ERRORS AND MAKE CUSTOM EXCEPTIONS

from exceptions.game_exceptions import *

class Action:
    def __init__(self, game, player, target=None, coins_needed=0):
        self.game = game
        self.player = player
        self.target = target
        self.coins_needed = coins_needed

    def execute(self):
        if self.player.coins < self.coins_needed:
            raise NotEnoughCoins(self.coins_needed)
        if self.target is not None and not self.target.hand:
                    raise InvalidTarget("Target is dead!")
    
    def perform_action(self):
        raise GameException("Method not implemented")


class Income(Action):
    def perform_action(self):
        self.player.coins += 1

class ForeignAid(Action):
    def perform_action(self):
        self.player.coins += 2

class Coup(Action):
    def __init__(self, game, player, target):
        super().__init__(game, player, target, coins_needed=7)

    def perform_action(self):
        super().execute()
        self.target.lose_influence()
        self.player.coins -= 7

class Tax(Action):
    def perform_action(self):
        self.player.coins += 3

class Assassinate(Action):
    def __init__(self, game, player, target):
        super().__init__(game, player, target, coins_needed=3)

    def perform_action(self):
        super().execute()
        self.target.lose_influence()
        self.player.coins -= 3

class Steal(Action):
    def __init__(self, game, player, target):
        super().__init__(game, player, target)

    def perform_action(self):
        super().execute()  # This will check for common conditions like if the target has influences left.

        if self.target.coins >= 2:
            stolen_coins = 2
        elif self.target.coins == 1:
            stolen_coins = 1
        else:
            raise GameException("Target has no coins to steal from.")

        self.target.coins -= stolen_coins
        self.player.coins += stolen_coins



class Exchange(Action):
    def __init__(self, game, player):
        super().__init__(game, player)

    def perform_action(self):

        if len(self.game.deck.cards) < 2:
            raise DeckEmptyException("Not enough cards in the deck to perform an exchange.")
            
        # Draw two cards from the deck
        drawn_cards = [self.game.deck.draw_card(), self.game.deck.draw_card()]

        # Add the two drawn cards to the players hand
        #self.player.hand.extend(drawn_cards)
        self.player.hand += drawn_cards

        # Return two cards back to the deck
        return drawn_cards




# def handle_exchange_action(game, player):
#     exchange_action = Exchange(game, player)
#     drawn_cards = exchange_action.perform_action()

#     # Show available cards (player's hand + drawn cards) and prompt for selection
#     print("Choose two cards to keep:")
#     # Example function to show and choose cards
#     kept_cards = player_choose_cards(player.hand + drawn_cards, 2)  

#     # Ensure correct number of cards are returned to the deck
#     if len(kept_cards) != 2:
#         raise GameException("Incorrect number of cards selected to keep.")

#     # Update the hand and return the rest of the cards to the deck
#     player.hand = kept_cards
#     returned_cards = [card for card in drawn_cards if card not in kept_cards]
#     for card in returned_cards:
#         game.deck.return_card(card)
#     game.deck.shuffle()


# This is for the game loop
# def handle_exchange_action(game, player):
#     exchange_action = Exchange(game, player)
#     drawn_cards = exchange_action.perform_action()

#     # Show all cards and prompt the player to choose which to keep
#     print(f"{player.name}, choose two cards to keep:")
#     for index, card in enumerate(player.hand, 1):
#         print(f"{index}. {card.name}")

#     # Assuming a function exists to get the player’s choices
#     kept_card_indices = get_player_card_selection(player, 2)
#     kept_cards = [player.hand[i] for i in kept_card_indices]

#     # Update the player's hand and return the remaining cards to the deck
#     player.hand = kept_cards
#     returned_cards = [card for card in drawn_cards if card not in kept_cards]

#     for card in returned_cards:
#         game.deck.return_card(card)
#     game.deck.shuffle()




    # def exchange(self, player):
    #     if not player.is_eliminated and not self.challenge(player, "exchange"):
    #         # Player exchanges cards with the court deck
    #         drawn_cards = [self.game.deck.draw_card() for _ in range(2)]
    #         player.hand.extend(drawn_cards)
    #         # Player must choose which cards to keep, returning two to the deck

    # def challenge(self, player, action):
    #     # Logic to handle a challenge
    #     challengers = [p for p in self.game.players if p != player and not p.is_eliminated]
    #     for challenger in challengers:
    #         if self.game.prompt_challenge(challenger, player, action):
    #             if player.has_card(action):
    #                 challenger.lose_influence()
    #                 self.game.deck.return_card(player.reveal_card(action))
    #                 return False
    #             else:
    #                 player.lose_influence()
    #                 return True
    #     return False

    # def block(self, player, action):
    #     # Logic to handle a block
    #     blockers = [p for p in self.game.players if p != player and not p.is_eliminated]
    #     for blocker in blockers:
    #         if self.game.prompt_block(blocker, player, action):
    #             if self.challenge(blocker, action):
    #                 return False
    #             return True
    #     return False
