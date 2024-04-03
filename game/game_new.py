from game.player_new import Player
from cards.deck import Deck
from actions.action_new import *
from exceptions.game_exceptions import *

class Game:
    """
    Represents the main game class for Coup, handling the game state, player actions, and game flow.
    """

    def __init__(self, deck):
        """
        Initializes the game with a set of players and a deck of cards.
        """
        self.players = []
        self.deck = deck
        self.current_player_index = 0
        self.game_over = False

    def setup(self):
        """
        Sets up the game by shuffling the deck and dealing cards and coins to each player.
        """
        self.deck.shuffle()
        for player in self.players:
            player.game = self
            player.add_card(self.deck.draw_card())
            player.add_card(self.deck.draw_card())
            #player.gain_coins(2)

    def is_game_over(self):
        """
        Checks if the game is over, which occurs when only one player remains.
        """
        return len(self.players_remaining()) <= 1

    def players_remaining(self):
        """
        Returns a list of players who are still in the game.
        """
        active_players = []
        for player in self.players:
            if not player.is_eliminated:
                active_players.append(player)
        return active_players

    def next_player(self):
        """
        Advances to the next player, skipping any who have been eliminated.
        """
        # Increment index by 1, if it reaches end of the list, loop back to 0
        print ("\n Next player's turn \n")
        self.current_player_index = (self.current_player_index + 1) % len(self.players)

        # Skip eliminated players
        while self.players[self.current_player_index].is_eliminated:
            self.current_player_index = (self.current_player_index + 1) % len(self.players)

    def end_game(self):
        """
        Ends the game and announces the winner.
        """
        self.game_over = True
        winner = self.players_remaining()[0]
        print(f"Game over! The winner is {winner.name}.")

    def force_coup(self, player):
        """
        Forces a coup if a player has 10 or more coins.
        """
        if player.get_coins() >= 10:
            print(f"{player.name} has 10 or more coins and must coup.")
            target = self.choose_target(player)
            Coup(self, player, target).perform_action()

    def play_game(self):
        """
        Main game loop that continues until the game is over.
        """
        while not self.is_game_over():
            self.play_turn(self.players[self.current_player_index])
            if self.game_over:
                break
            self.next_player()

        self.end_game()

    def play_turn(self, player):
        """
        Executes a single turn for the given player.
        """
        print(f"{player.name}'s turn. Coins: {player.get_coins()}")
        player.display_cards(player.hand)
        self.force_coup(player)
        if not player.is_eliminated:
            self.execute_action(player)

    def execute_action(self, player):
        """
        Manages the execution of a player's action, including challenges and blocks.
        """

        action = self.choose_action(player)
        target_description = f"on {action.target.name}" if action.target else ""
        print(f"{player.name} is attempting to perform {action.action_name}{target_description}.")

        #print(f"{player.name} is attempting to perform {action.action_name} on {action.target.name if action.target else 'no one'}.")

        # If action requires an influence, then prompt players if they wish to challenge
        if action.requires_influence:
            challenger = self.prompt_challenge(player, action)
            # If there is a challenger
            if challenger:
                # Handle the challenge and return the result. (Handle challenge deals with losing influence, swapping card etc)
                challenge_result = self.handle_challenge(player, challenger, action.required_card)
                if not challenge_result: # If Challenger has won, The player has lost a card (handled above), and the turn has ended
                    print(f"Turn ends. {challenger.name} has won the challenge.")
                    return
                else: # If player has won the challenge. (Challenger has lost an influence. this happened in handle challenge)
                    if self.is_game_over(): # Check if 1 player remaining, if so then the game is over. (Turn ends here)
                        self.game_over = True
                        return
                    if action.target and action.target.is_eliminated: # If there is a target, and target is eliminated, then the turn ends.
                        print(f"Turn ends. {action.target.name} has been eliminated.")
                        return
                    
        # TODO If ction is assassination, pay coins, and move onto block phase. dont perform action yet:
        if action.is_blockable:
            self.handle_block_phase(action, player)
        else:
            action.perform_action()




    # def handle_block_phase(self, action, player):
    #     # Handles block portion and challenge block.
    #     """
    #     Handles the players block phase.
    #     """
    #     blocker = None

    #     if action.action_name == "Foreign Aid": # Prompt block to everyone
    #         print(f"{player.name} is attempting to perform Foreign Aid. Who wants to block by claiming they have Duke?")
    #         # TODO wants to block should return a can block card as an available action.
    #         blocker = self.prompt_block(player, action) # Returns blocker
    #         if blocker:
    #             player_challenges_blocker = self.wants_to_challenge(player, blocker, "Duke") #does player want to challenge blocker claim card?
    #             if player_challenges_blocker: # If player wants to challenge
    #                 challenge_block_result = self.handle_challenge(blocker, player, blocker_claim_card)
    #                 if not challenge_block_result: # If player wins challenge
    #                     # Player performs action and turn ends
    #                     action.perform_action() #END
    #                     return
    #                 else: # If player loses challenge
    #                     print(f"Turn ends. {blocker.name} has successfully blocked {player.name}'s {action.name}.")
    #                     return
    #             else: # If player does not challenge blocker
    #                 print("Turn ends. Blocker is not challenged.")
    #                 return
                
    #         # No blocker, player performs action and ends turn
    #         action.perform_action()
    #         return
        
    #     else: #For all other actions (Assassinate, and steal)
    #         if action.is_blockable and not player.is_eliminated: #is the and not player is eliminated needed here.
    #             # TODO Wants to block should prompt to block with a can block card. this card is the action they wish to play
    #             if self.wants_to_block(action.target, player, action): #Prompt the target if they wish to block
    #                 blocker = action.target # If they do, set blocker to the target.

    #                 player_challenges_blocker = self.wants_to_challenge(player, blocker, blocker_claim_card)
    #                 if player_challenges_blocker:
    #                     challenge_block_result = self.handle_challenge(blocker, player, blocker_claim_card)
    #                     if not challenge_block_result: # If player has won the challenge
    #                         if blocker.is_eliminated: # If blocker is eliminated, end turn
    #                             print(f"Turn ends. {blocker.name} has been eliminated.")
    #                             return
    #                         else: # If blocker is not eliminated, perform action
    #                             action.perform_action()
    #                             return
    #                     else: # If player has lost the challenge
    #                         # Action is blocked, end turn
    #                         print(f"Turn ends. {blocker.name} has successfully blocked {player.name}'s {action.name}.")
    #                         return
    #                 else: # If player does not challenge blocker
    #                     print("Turn ends. Blocker is not challenged.")
    #                     return
    #         # No blocker, player performs action and ends turn
    #         action.perform_action()
    #         return
        
    def handle_block_phase(self, action, player):
        blocker, blocker_claim_card = self.prompt_block(player, action)

        if blocker:
            print(f"{blocker.name} has chosen to block with {blocker_claim_card}.")
            if self.wants_to_challenge(player, blocker, blocker_claim_card):
                blocker_wins_challenge = self.handle_challenge(blocker, player, blocker_claim_card)
                if blocker_wins_challenge:  # If blocker (the one being challenged) wins the challenge
                    print(f"Turn ends. {blocker.name} has successfully defended their claim and blocked the action.")
                    return  # Exits the function
                else:  # If the player (the challenger) wins the challenge
                    if action.target and action.target.is_eliminated:
                        print(f"Turn ends. {action.target.name} has been eliminated.")
                        return  # Exits the function
                    else:
                        print(f"{player.name} has won the challenge and moves to perform {action.action_name}.")
                        action.perform_action()  # Perform action
            else:  # If player does not challenge blocker
                print("Turn ends. Blocker's claim is unchallenged.")
                return  # Exits the function
        else:  # If no blocker
            print(f"No blocker, {player.name} will perform {action.action_name}.")

            action.perform_action()





        
    def wants_to_challenge(self, challenger, player, action_name):
        """
        Prompts a player to decide whether to challenge an action or a claim (e.g., "Duke" for blocking Foreign Aid).
        """
        # Determine what is being challenged: an action or a claim

        print(f"{challenger.name}, do you want to challenge {player.name}'s claim of {action_name}?")
        while True:
            decision = input("Type y for yes, n for no: ").strip().lower()
            if decision == 'y':
                return decision
            elif decision == 'n':
                return None
            else:
                print("Invalid input, please enter 'y' for yes or 'n' for no.")


    def wants_to_block(self, blocker, player, action):
        """
        Prompts a player to decide whether to block a players action.
        """
        # Blocking means you claim one of the following cards:
        # Duke, Captain, Ambassador, Contessa.
        # Maybe say do you want to block action with [can be blocked cards?]
        print(f"{blocker.name}, do you want to block {player.name}'s {action.action_name}?")
        while True:
            decision = input("Type y for yes, n for no: ").strip().lower()
            if decision == 'y':
                return decision
            elif decision == 'n':
                return None
            else:
                print("Invalid input, please enter 'y' for yes or 'n' for no.")
    
    def prompt_challenge(self, player, action):
        """
        Prompts for a challenge against a player's action.
        """
        for challenger in self.players_remaining():
            if challenger != player and self.wants_to_challenge(challenger, player, action.required_card):
                return challenger
        return None
    

    def prompt_block(self, player, action):
        if action.action_name == "Foreign Aid":
            print(f"{player.name} is attempting Foreign Aid. Who wants to block by claiming Duke?")
            for potential_blocker in self.players_remaining():
                if potential_blocker != player and self.wants_to_block(potential_blocker, player, action):
                    return potential_blocker, "Duke"
        else:
            if action.target and self.wants_to_block(action.target, player, action):
                print(f"{action.target.name}, which card do you claim to block with?")
                for card in action.can_block:
                    print(f"- Claim {card}")
                chosen_card = self.get_block_choice(action.target, action.can_block)
                if chosen_card:
                    return action.target, chosen_card

        return None, None

    def get_block_choice(self, player, block_options):
        """
        Prompts the player to choose a card to claim for blocking an action.
        :param player: The player who is choosing the card.
        :param block_options: A list of cards that the player can claim to block with.
        :return: The chosen card or None if the player does not choose a valid option.
        """
        print(f"{player.name}, choose a card to block with:")
        for i, option in enumerate(block_options, 1):
            print(f"{i}: {option}")

        while True:
            choice = input("Enter the number of the card you wish to claim: ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(block_options):
                return block_options[int(choice) - 1]
            else:
                print("Invalid choice, please select a valid card number.")



    def handle_challenge(self, player, challenger, card_name):
        # Always able to choose what card to lose.
        """
        Manages the challenge process between players over an action.
        Returns True if the player wins, False if the challenger wins.

        """

        # Check if the challenged player has the card
        if player.has_card(card_name):
            # Player can choose to show or not show the card.
            if player.prompt_show_card(card_name): # If player chooses to show card
                print(f"{player.name} has successfully shown {card_name} and wins challenge.")
                player.swap_card(player.get_card_index(card_name))
                challenger.lose_influence()
                return True # Player wins the challenge


        print(f"{player.name} either does not have {card_name} or chooses not to show it and loses the challenge.")
        player.lose_influence()
        return False #  Challenger wins the challenge

    
                
    # def choose_action(self, player):
    #     # Dictionary of available actions, with an indication if they need a target
    #     actions = {
    #         "1": {"action": Income(self, player), "needs_target": False},
    #         "2": {"action": ForeignAid(self, player), "needs_target": False},
    #         "3": {"action": Coup(self, player, None), "needs_target": True},  # Target is initially None
    #         "4": {"action": Tax(self, player), "needs_target": False},
    #         "5": {"action": Assassinate(self, player, None), "needs_target": True},  # Target is initially None
    #         "6": {"action": Steal(self, player, None), "needs_target": True},  # Target is initially None
    #         "7": {"action": Exchange(self, player), "needs_target": False}
    #     }

    #     valid_actions = []

    #     while True:
    #         print("Note: Some actions will require you to choose a target next.")
    #         # Display available actions
    #         print(f"{player.name}, choose an action:")
    #         for key, val in actions.items():
    #             action_note = "(needs to choose target next)" if val["needs_target"] else ""
    #             print(f"{key}: {val['action'].action_name} {action_note}")

    #         # Player chooses an action
    #         choice = input("Enter the number of the action you want to perform: ").strip()
    #         if choice in actions:
    #             selected_action = actions[choice]["action"]
    #             needs_target = actions[choice]["needs_target"]
                
    #             # If the chosen action needs a target, prompt for it
    #             if needs_target:
    #                 target = self.choose_target(player)
    #                 if target is None:  # No valid target available
    #                     print("No valid targets available. Please choose a different action.")
    #                     continue  # Return to the start of the while loop to choose another action
    #                 selected_action.target = target  # Set the target for the action
                        
    #             return selected_action  # Action is selected and, if needed, has a valid target
    #         else:
    #             print("Invalid choice, please enter a valid number.")


    def choose_action(self, player):
        # Dictionary of available actions, with an indication if they need a target
        actions = {
            "1": {"action": Income(self, player), "needs_target": False},
            "2": {"action": ForeignAid(self, player), "needs_target": False},
            "3": {"action": Coup(self, player, None), "needs_target": True},  # Target is initially None
            "4": {"action": Tax(self, player), "needs_target": False},
            "5": {"action": Assassinate(self, player, None), "needs_target": True},  # Target is initially None
            "6": {"action": Steal(self, player, None), "needs_target": True},  # Target is initially None
            "7": {"action": Exchange(self, player), "needs_target": False}
        }

        valid_actions = []  # List to store actions the player can afford

        for key, val in actions.items():
            action = val["action"]
            if action.coins_needed <= player.get_coins():  # Check if player can afford the action
                valid_actions.append((key, val))

        if not valid_actions:
            print("You don't have enough coins to perform any action.")
            return None

        while True:
            print("\n \n Note: Some actions will require you to choose a target next.")
            # Display available actions the player can afford with indexes in order
            print(f"{player.name}, choose an action:")
            for index, (key, val) in enumerate(valid_actions, start=1):
                action_note = "(needs to choose target next)" if val["needs_target"] else ""
                print(f"{index}: {val['action'].action_name} {action_note}")

            # Player chooses an action
            choice = input("Enter the number of the action you want to perform: ").strip()
            try:
                index = int(choice)
                if 1 <= index <= len(valid_actions):
                    selected_action = valid_actions[index - 1][1]["action"]
                    needs_target = valid_actions[index - 1][1]["needs_target"]

                    # If the chosen action needs a target, prompt for it
                    if needs_target:
                        target = self.choose_target(player)
                        if target is None:  # No valid target available
                            print("No valid targets available. Please choose a different action.")
                            continue  # Return to the start of the while loop to choose another action
                        selected_action.target = target  # Set the target for the action

                    return selected_action  # Action is selected and, if needed, has a valid target
                else:
                    print("Invalid choice, please enter a valid number.")
            except ValueError:
                print("Invalid input, please enter a number.")




    def choose_target(self, player):
        valid_targets = []
        for x in self.players:
            if x != player and not x.is_eliminated:
                valid_targets.append(x)

        if not valid_targets:
            print("No valid targets available.")
            return None

        print("Choose a target:")
        for i, target in enumerate(valid_targets, 1):
            print(f"{i}: {target.name}")

        while True:
            try:
                choice = int(input("Enter the number of the target you want to choose: ").strip())
                if 1 <= choice <= len(valid_targets):
                    return valid_targets[choice - 1]
                else:
                    print("Invalid choice, please select a number from the list.")
            except ValueError:
                print("Invalid input, please enter a number.")



if __name__ == "__main__":
    # Example setup
    deck = Deck()
    game = Game([], deck)  # Initialize game with an empty list of players
    players = [Player(f"Player {i}", game) for i in range(4)]  # Pass game to Player constructor
    game.players = players  # Assign the players to the game


