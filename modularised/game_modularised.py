from cards.deck import Deck
from modularised.action_modularised import Coup  # Ensure actions are correctly imported
from exceptions.game_exceptions import *
from game.game_ui import GameUI

class Game:
    def __init__(self, players, deck, ui):
        self.players = players
        self.deck = deck
        self.ui = ui
        self.current_player_index = 0
        self.game_over = False

    def setup(self):
        self.deck.shuffle()
        for player in self.players:
            player.set_game(self)
            player.add_card(self.deck.draw_card())
            player.add_card(self.deck.draw_card())

    def is_game_over(self):
        return len(self.players_remaining()) <= 1

    def players_remaining(self):
        return [player for player in self.players if not player.is_eliminated]

    def next_player(self):
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        while self.players[self.current_player_index].is_eliminated:
            self.current_player_index = (self.current_player_index + 1) % len(self.players)

    def end_game(self):
        self.game_over = True
        winner = self.players_remaining()[0]
        self.ui.show_end_game(winner)

    def force_coup(self, player):
        if player.get_coins() >= 10:
            self.ui.display_message(f"{player.name} has 10 or more coins and must coup.")
            target = self.choose_target(player)
            Coup(self, player, target).perform_action()

    def play_game(self):
        self.ui.display_title()
        while not self.is_game_over():
            self.play_turn(self.players[self.current_player_index])
            if self.game_over:
                break
            self.next_player()

        self.end_game()

    def play_turn(self, player):
        self.ui.display_game_state(self.players, self.deck)
        self.force_coup(player)
        if not player.is_eliminated:
            self.execute_action(player)

    def execute_action(self, player):
        action = player.choose_action()  # no need to pass self.ui
        self.ui.announce_action_result(player, action, True)  # Assuming action succeeds for now

        if action.requires_influence and player.wants_to_challenge(action):
            challenge_result = self.handle_challenge(player, player.challenge_action(action), action.required_card)
            if not challenge_result:
                return

        if action.is_blockable:
            self.handle_block_phase(action, player)
        else:
            action.perform_action()


    def handle_block_phase(self, action, player):
        blocker = player.decide_block(action)
        if blocker:
            if player.wants_to_challenge(action):
                if not self.handle_challenge(blocker, player, action.required_card):
                    return
            action.perform_action()

    def handle_challenge(self, player, challenger, card_name):
        if player.has_card(card_name) and player.prompt_show_card(card_name):
            player.swap_card(player.get_card_index(card_name))
            challenger.lose_influence()
            return True

        player.lose_influence()
        return False

    def choose_target(self, player):
        return player.choose_target(self.players_remaining())

    def available_actions(self, player):
        # Example implementation, adjust based on your game's logic
        actions = ['Income', 'Foreign Aid']  # Placeholder for actual action objects or names
        if player.get_coins() >= 7:
            actions.append('Coup')
        # Add more actions based on game and player state
        return actions
    
