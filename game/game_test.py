from player import Player
from cards.deck import Deck
from action import *
from exceptions.game_exceptions import *


class Game:
    def __init__(self, players, deck):
        self.players = players
        self.deck = deck #should this be self.deck = Deck() ?
        self.current_player_index = 0
        self.game_over = False
        self.setup()

    def setup(self): 
        # Shuffle the deck, deal two cards to each player, and set starting coins
        self.deck.shuffle()
        for player in self.players:
            player.hand.append(self.deck.draw_card())
            player.hand.append(self.deck.draw_card())
            player.coins = 2

    def is_game_over(self):
        active_players = self.players_remaining()
        return len(active_players) <= 1
    
    def players_remaining(self):
        active_players = []
        for player in self.players:
            if not player.is_eliminated:
                active_players.append(player)
        return active_players
    
    def next_player(self):
        # Increment index by 1, if it reaches end of the list, loop back to 0
        self.current_player_index = (self.current_player_index + 1) % len(self.players)

        # Skip eliminated players
        while self.players[self.current_player_index].is_eliminated:
            self.current_player_index = (self.current_player_index + 1) % len(self.players)

            
    def end_game(self):
        self.game_over = True
        winner = self.players_remaining()[0]
        print(f"Game over! The winner is {winner.name}.")
        # consider more things to add?

    def force_coup(self, player):
        #do we need validation checks here
        print(f"{player.name} has 10 or more coins and must coup.")
        target = self.choose_target(player)
        Coup(self, player, target).perform_action()

    def play_game(self):
        while not self.is_game_over():
            self.play_turn(self.players[self.current_player_index])
            if self.game_over:
                break  # End the game loop if the game has ended
            self.next_player()

        if self.is_game_over():
            self.end_game()

    def play_turn(self, player):
        # If player has 10 or more coins, must coup
        if player.get_coins() >= 10:
            self.force_coup(player)
        else:
            self.execute_action(player)

    def choose_action(self, player):
        pass

    def execute_action(self, player):
        # 1. Current player chooses action
        action = self.choose_action(player)
        # 2. Does action require character influence?
        if action.requires_influence:
            # 2a. Is action challenged?
            challenger = self.prompt_challenge(player, action)
            # If there is a challenger, execute challenge
            if challenger:
                # Returns False if challenger loses challenge. (Player wins)
                challenge_result = self.handle_challenge(player, challenger, action)
                if not challenge_result: #If player wins challenge, challenger loses influence
                    if self.is_game_over(): # Check if 1 player remaining
                        self.game_over = True
                        return
                    print("Move to block check")
                    
                else:
                    # Challenger wins the challenge
                    print("Turn ends.")
                    return #Turn ends
                
        # If action can be blocked, proceed to block check
        # Only the target can block the action.
        if action.is_blockable and not player.is_eliminated:
            # Prompt target to block action
            blocker = self.prompt_block(action.target, player, action)
            # If target wishes to block action, execute block
            if blocker:
                # Does player want to challenge blocker?
                player_challenge_blocker = self.wants_to_challenge(player, blocker, action)
                #player_challenge_block = self.prompt_challenge_block(player, blocker, action)
                if player_challenge_blocker: #If player whishes to challenge blocker
                    # Player challenges the blocker
                    challenge_block_result = self.handle_challenge(blocker, player, action)
                    # If player wins this challenge it will return true here
                    if challenge_block_result: #If player wins challenge (blocker loses influence)
                        if self.is_game_over(): # Check if 1 player remaining
                            self.game_over = True
                            return
                        print(f"{player.name} now moves to perform action")
                    else: # If blocker wins the challenge
                        print("Turn ends.")
                        return # Turn ends
                else: # If player does not challenge blocker
                    return #Turn ends as player does not challenge blocker
        # Player performs action
        if not player.is_eliminated:
            action.perform_action(action)

    def wants_to_challenge(self, challenger, player, action):
        # This method should ask the challenger if they want to challenge the action
        print(f"{challenger.name}, do you want to challenge {player.name}'s {action.name}?")
        response = input("Type 'yes' to challenge, anything else to skip: ").strip().lower()
        return response == 'yes'

    def prompt_challenge(self, player, action):
        # Prompt the target first if they wish to challenge, otherwise prompt rest of alive players
        if action.target and self.wants_to_challenge(action.target, player, action):
            return action.target

        # If the target player does not challenge, ask the other players
        for challenger in self.players_remaining():
            # Skip the action's player and the target since they've already been prompted
            if challenger == player or challenger == action.target:
                continue

            if self.wants_to_challenge(challenger, player, action):
                return challenger

        # No one challenged
        return None

    def prompt_block(self, target, player, action):
        print(f"{target.name}, do you want to block {player.name}'s {action.name}?")
        while True:
            decision = input("Type y for yes, n for no: ").strip().lower()
            if decision == 'y':
                return target
            elif decision == 'n':
                return None
            else:
                print("Invalid input, please enter 'y' for yes or 'n' for no.")

    
        """
        Return false if challenger loses challenge. (Player wins)
        If player has the influence challenged:
            If player wants to show the card
                return false (Player wins)
            If player does not want to show the card
                return true (Player loses)
        (assuming player does not have the influence card)
            return true (Player loses)

        """
    def handle_challenge(self, player, challenger, action):
        card_name = action.required_card
        card_index = player.show_card(card_name)

        if card_index is not None:
            while True:
                decision = input(f"{player.name}, do you want to show the {action.action_name} card to win the challenge? (y/n): ").strip().lower()
                if decision == 'y':
                    print(f"{player.name} has shown the {card_name} card to win the challenge.")
                    challenger.lose_influence()
                    player.swap_card(card_index)
                    return False
                elif decision == 'n':
                    print(f"{player.name} has lost the challenge")
                    player.lose_influence()
                    return True
                else:
                    print("Invalid input, please enter 'y' for yes or 'n' for no.")
        else:
            print(f"{player.name} does not have the {card_name} card and has lost the challenge")
            player.lose_influence()
            return True

    # def choose_action(self, player):
    #     # List of available actions
    #     actions = {
    #         "1": Income(self, player),
    #         "2": ForeignAid(self, player),
    #         "3": Coup(self, player, self.choose_target(player)),  # Assuming choose_target is implemented
    #         "4": Tax(self, player),
    #         "5": Assassinate(self, player, self.choose_target(player)),
    #         "6": Steal(self, player, self.choose_target(player)),
    #         "7": Exchange(self, player)
    #     }

    #     # Display available actions
    #     print(f"{player.name}, choose an action:")
    #     for key, action in actions.items():
    #         print(f"{key}: {action.action_name}")

    #     # Player chooses an action
    #     while True:
    #         choice = input("Enter the number of the action you want to perform: ").strip()
    #         if choice in actions:
    #             return actions[choice]
    #         else:
    #             print("Invalid choice, please enter a valid number.")

    # # Example usage of choose_target, assuming you need to select a target for some actions
    # def choose_target(self, player):
    #     print(f"{player.name}, choose a target for your action:")
    #     potential_targets = [p for p in self.players if p != player and not p.is_eliminated]
    #     for i, target in enumerate(potential_targets, 1):
    #         print(f"{i}: {target.name}")

    #     while True:
    #         target_choice = input("Enter the number of the player you want to target: ").strip()
    #         if target_choice.isdigit() and 1 <= int(target_choice) <= len(potential_targets):
    #             return potential_targets[int(target_choice) - 1]
    #         else:
    #             print("Invalid choice, please enter a valid number.")
