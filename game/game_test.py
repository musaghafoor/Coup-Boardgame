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

        # TODO Remove the results of handling challenge. let handle challenge handle it.
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
                if not challenge_result: #If player wins challenge
                    # Challenging player loses influence
                    # Player changes card
                    challenger.lose_influence() #If last card, then challenger will be eliminated. (handled in player class)
                    player.change_card() # Player returns card to deck and receives random card
                    print(f"{player.name} has won the challenge. Move to block check")
                else:
                    # Challenger wins the challenge
                    # Player loses influence
                    player.lose_influence() #If last card, then player will be eliminated. (handled in player class)
                    print(f"{player.name} has lost the challenge. Turn ends.")
                    return #Turn ends
                
        # If action can be blocked, proceed to block check
        # Only the target can block the action.
        if action.is_blockable and not player.is_eliminated:
            # Prompt target to block action
            blocker = self.prompt_block(action.target, action)
            # If target wishes to block action, execute block
            if blocker:
                # Does player challenge blocker?
                player_challenge_block = self.prompt_challenge_block(player, blocker, action)
                if player_challenge_block: #If player whishes to challenge blocker
                    # Player challenges the blocker
                    challenge_block_result = self.handle_challenge(blocker, player, action)
                    # If player wins this challenge it will return true here
                    if challenge_block_result: #If player wins challenge
                        blocker.lose_influence() #If last card, then blocker will be eliminated. (handled in player class)
                    else: # If blocker wins the challenge
                        player.lose_influence() #If last card, then player will be eliminated. (handled in player class)
                        blocker.change_card() # blocker returns card to deck and receives random card
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




    def handle_challenge(self, player, challenger, action):
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
        pass

    # TODO Handle losing cards etc. Also find a way to check if player has action card.
    def handle_challenge(self, player, challenger, action):

        # Check if the player has the card they claimed to have
        if player.has_card(action.required_card):
            # Prompt player to decide whether to show the card
            if self.prompt_show_card(player, action.required_card):
                print(f"{player.name} has shown {action.required_card} to prove the action.")
                
                # Player shows the card, challenger loses an influence
                challenger.lose_influence()
                if challenger.is_eliminated:
                    print(f"{challenger.name} is eliminated!")

                # Player swaps the shown card with a new one from the deck
                player.swap_card(action.required_card)
                return False  # Challenger loses the challenge
            else:
                print(f"{player.name} has decided not to show the card.")
        else:
            print(f"{player.name} does not have the required card for the action.")

        # Player loses an influence because they either chose not to show the card or didn't have it
        player.lose_influence()
        if player.is_eliminated:
            print(f"{player.name} is eliminated!")

        return True  # Challenger wins the challenge

    def prompt_show_card(self, player, card):
        """
        Asks the player if they want to show the card to counter the challenge.

        :param player: The player who is being prompted.
        :param card: The card in question.
        :return: True if the player decides to show the card, False otherwise.
        """
        response = input(f"{player.name}, do you want to show the {card} to counter the challenge? (yes/no): ")
        return response.strip().lower() == 'yes'

