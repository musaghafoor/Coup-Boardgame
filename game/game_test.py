from player import Player
from cards.deck import Deck
from action import *
from exceptions.game_exceptions import *
"""
TODO:
Implement the following:
- Initialising the game state
- Running the main game loop
- Handling player turns
- Handling player actions
- Handling player reactions (blocks, challenges and counteractions)
- For challenging, after a player wins the challenge, ensure that their card is shown and then returned to the deck, and a new card is drawn
- For assassin challenges, two cards can be lost if the challenge attempt is unsuccessful (lose challenge and action is played)
- Ensure that their is a counteraction. For example if target is challenged, they can counteract with a card. (e.g if assasssin action is played, they can block with contessa. This block can be challenged)
- Checking for game over conditions
- Handling game over
https://www.ultraboardgames.com/coup/game-rules.php
"""

#have a dictionary to display and store all lost influences (when eliminated) with the player name next to it
#Only the player being assassinated can use (or bluff) a Contessa to block their own assassination
#When a player has lost all their influence and both their cards are face up in front of them, 
#they are immediately out of the game. They leave their cards face up and return all their coins to the Treasury.
#TODO MAKE SURE THAT WE HAVE MAX COINS FOR TREASURY. IF NO COINS TO WITHDRAW THEN MUST INCLUDE CHOOSE NAOTHER ACTION
"""
Steps:
Initialise game state first:
    - Create a deck of cards
    - Create a list of players
    - Assign cards to players
    - Assign coins to players
    - Track current player

Game loop:
    - Check if game is over
    - If not, execute turn for current player
    - Check if player eliminated?
    - Check if game over
    - Next player turn

Execute turn:
    - If player has 10 or more coins, forced to coup
    - Otherwise, list actions 
    - Choose action
    - If action can be blocked:
        - Show prompt for all other active players to block or challenge
        - If action is blocked:
            - Handle block check (in block it can challenge again)
    - If action can be challenged (idk how this differs from block?)
        - Handle challenge check
    - Execute action 
    
Handle block:
(block should show contessa as an option. e.g if assassin is played, they can block with contessa. does not require player to have contessa in hand.)
    - Target blocks player with a card
    - Player can challenge target's card
        -If player wants to challenge,
            -Challenge target card
            if challenge successful:
            -Remove influence from target
            if not:
                Remove influence from player
                action blocked.
        Otherwise, block action

Chalenge:
    - we have player and challenger and the challenged card
    - if player wants to reveal the challenged card:
        - show challenged card
        - player.change card (shuffle the challenged card back into deck and draw a new card)
        - challenger loses influence
        - action proceeds
    - if player does not want to reveal a card:
        player loses one influence, and that card is shown
        action is blocked
"""

"""
 1. Check if player is alive. If not, throw exception.
        2. Check if player has at least 12 coins. If they do, throw exception unless coup is played.
        3. Check if any player wants to call bluff from active player
           a. If someone wants to call bluff, do Call step
        4. Check if a player wants to block
           a. If active player wants to call bluff, do Call step (todo: official rules says any play can call bluff. implement later)
        5. Play action if successful
        Call step: If someone call the bluff, reveal card. 
                   If card is the action played, remove influence from player.
                   Else, remove influence from calling player  
"""

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

            """
        1. Current player takes action
        2. Does action requires character influence :
            Yes:
                2a. Is action challenged?
                    Yes:
                        2a.i Does player display the card? (may choose to not reveal card)
                            Yes:
                                2a.i.1 Challenging player losees influence
                                2a.i.2 Current player changes card
                                Proceed to 2b (block check)
                            No:
                                2a.i.1 Current player loses influence
                                2a.i.2 Current player does not proceed with action and turn ends
            No:
                2b. Is action blocked?
                    Yes:
                        2b.i Does player (current player) challenge block
                            Yes:
                                2b.i.1 Does blocking player display the card? (may choose to not reveal card)
                                    Yes:
                                        2b.i.1.1 Challenging player (current player) loses influence
                                        2b.i.1.2 Blocking player changes card
                                        Turn end
                                    No:
                                        2b.i.1.1 Blocking player loses influence
                                        Resolve action (current player executes action)
                            No:
                                Turn end (current player does not execute action)
                    No:
                        Resolve action (current player executes action)

            
        """
            
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
            blocker = self.prompt_block(action.target, player, action) # TODO get blocker to choose what to block with?
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
            action.perform_action()

    def wants_to_challenge(self, challenger, player, action):
        # This method should ask the challenger if they want to challenge the action
        print(f"{challenger.name}, do you want to challenge {player.name}'s {action.name}?")
        while True:
            decision = input("Type y for yes, n for no: ").strip().lower()
            if decision == 'y':
                return decision
            elif decision == 'n':
                return None
            else:
                print("Invalid input, please enter 'y' for yes or 'n' for no.")

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

        print("Note: Some actions will require you to choose a target next.")
        # Display available actions
        print(f"{player.name}, choose an action:")
        for key, val in actions.items():
            action_note = "(needs to choose target next)" if val["needs_target"] else ""
            print(f"{key}: {val['action'].action_name} {action_note}")

        # Player chooses an action
        while True:
            choice = input("Enter the number of the action you want to perform: ").strip()
            if choice in actions:
                selected_action = actions[choice]["action"]
                needs_target = actions[choice]["needs_target"]
                
                # If the chosen action needs a target, prompt for it
                if needs_target:
                    target = self.choose_target(player)
                    selected_action.target = target  # Assuming the action has a 'target' attribute to be set
                    
                return selected_action
            else:
                print("Invalid choice, please enter a valid number.")

    def choose_target(self, player):
        # Assuming there is a list of players named self.players
        # Would exclude the current player from being a target
        targets = [p for p in self.players if p != player and not p.is_eliminated]
        print("Choose a target:")
        for key, target_player in targets.items():
            print(f"{key}: {target_player.name}")

        while True:
            target_choice = input().strip()
            if target_choice in targets:
                return targets[target_choice]
            else:
                print("Invalid choice, please try again.")

if __name__ == "__main__":
    game = Game(num_players=4)
    game.run()