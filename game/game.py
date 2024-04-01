from player import Player
from cards.deck import Deck
from action import *

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
class Game_R:
    def __init__(self, number_of_players):
        self.players = []
        #Maybe have something where player is prompted to name themselves?

        for i in range(1, number_of_players + 1):
            player_name = "Player " + str(i)
            self.players.append(Player(player_name))
        
        self.deck = Deck()
        self.current_turn = 0
        self.game_over = False
        #self.active_player = self.players[self.current_turn]
        self.current_player_index = 0
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
    
    def play_turn(self):
        player = self.players[self.current_player_index]
        if player.get_coins() >= 10:
            self.force_coup(player)
        else:
            self.execute_action(player)

    def force_coup(self, player):
        print(f"{player.name} has 10 or more coins and must coup.")
        target = self.choose_target(player)
        Coup(self, player, target).perform_action()

    

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
    #is_blockable means is challengable
    #
    def execute_action(self, player):
        action = self.choose_action(player)
        # If the action requires an influence, it can be challenged.
        if action.requires_influence:
            challenger = self.prompt_public_challenge(player, action)
            if challenger:
                challenge_successful = self.handle_challenge(player, challenger, action)
                if not challenge_successful:
                    return #challenge successful
        
                
        #If action can be blocked, call handle block
        if action.is_blockable:
            blocker = self.prompt_block(player, action)
            if blocker:
                block_successful = self.handle_block(player, blocker, action)
                if not block_successful:
                    return #block successful

        action.perform_action(action)
        #execute action either performs action or does not perform action based on above
        pass

    def prompt_public_challenge(self, current_player, action):
        if action.action_name == "Assassinate":
            #maybe print saying player is attempting to assassinate target?
            target = action.target
            if target.wants_to_challenge(current_player, action):
                print(f"{target.name} has chosen to challenge!")
                return target #maybe say target doesnt want to challenge and might ahve to block to live or something
        else:
            print(f"{current_player.name} is attempting to perform {action.name}.")
            for challenger in self.players_remaining():
                if challenger != current_player:
                    # make this method ??
                    if challenger.wants_to_challenge(current_player, action):
                        print(f"{challenger.name} has chosen to challenge {current_player.name}'s {action.name}!")
                        return challenger
        print("No one has chosen to challenge.")
        return None
    
    def prompt_block_challenge(self, current_player, blocker, action):
        if current_player.wants_to_challenge(blocker, action):
            return current_player
        return None

    
    def hande_challenge(self, player, challenger, action):
        
        pass

    

    def handle_challenge(self, player, action):
        #should prompt for users to challenge players action. Maybe call prompt challenge
        #if user wishes to challenge then
            # challenger = user who wishes to challenge
            # Does player display the card? (may choose to not reveal card)
            #yes:
                #    challenger loses influence
                #    player swaps cards
                #    returns  back to execute action and goes to next step (is blockable)
            #no:
                #    player loses influence
                #    coins returned back to player/ action does not execute
                #    returns back to exectute action and does not perform action
        #if no user wishes to challenge then return back to execute action and go to next step (is blockable)
        
        pass

    def handle_block(self, player, action):
        #should prompt for users to block players action. Maybe call prompt block
        #if user wishes to block then
            # blocker = user who wishes to block
            # Is blocking challenged? (prompt?)
                # yes:
                    # Does blocking player display the card? (may choose to not reveal card)
                    # yes:
                        #    challenger loses influence
                        #    blocking player swaps cards
                        #    returns back to execute action where it ends player turn (does not perform action)
                    # no:
                        #    blocking player loses influence
                        #    go back to execute action where player performs action
        #if no user wish to block:
            # go back to execute action where action is executed

        
        



    def run(self):
        # Main game loop
        while not self.game_over:
            self.active_player = self.players[self.current_turn]
            if not self.active_player.is_eliminated:
                self.execute_turn(self.active_player)
            self.check_game_over()
            self.current_turn = (self.current_turn + 1) % len(self.players)

    def execute_turn(self, player): 
        # Perform the actions of the current player's turn
        print(f"\n{player}'s turn.")
        chosen_action = self.choose_action(player)
        try:
            # Check for challenges here before executing the action
            self.handle_challenges(chosen_action)
            chosen_action.perform_action()
            # Check for blocks here after executing the action if not challenged or challenge failed
            self.handle_blocks(chosen_action)
        except GameException as e:
            print(str(e))
            # Depending on game rules, you may want to retry the turn or simply pass to the next player
            return
        
    def get_available_actions(self, player):
        actions = [Income(self, player), ForeignAid(self, player)]

        if player.coins >= 3:  # Assume 3 coins are needed to perform an Assassinate
            actions.append(Assassinate(self, player, None))  # Target is to be decided later

        if player.coins >= 7:  # Assume 7 coins are needed to perform a Coup
            actions.append(Coup(self, player, None))

        actions.extend([Tax(self, player), Steal(self, player, None), Exchange(self, player)])

        return actions
    
    def display_available_actions(self, player, available_actions):
        print(f"\n{player.name}, choose your action:")
        for index, action in enumerate(available_actions, 1):
            print(f"{index}. {action.__class__.__name__}")


    def choose_action(self, player):
        if player.coins >= 10:
            print("You have 10 or more coins and must perform a coup.")
            return Coup(self, player, self.choose_target(player))
    
        available_actions = self.get_available_actions(player)
        self.display_available_actions(player, available_actions)
    
        while True:
            choice = input("Choose your action: ")
            if choice.isdigit() and 0 < int(choice) <= len(available_actions):
                selected_action = available_actions[int(choice) - 1]
                if isinstance(selected_action, Coup):
                    target = self.choose_target(player)
                    if target:
                        return Coup(self, player, target)
                else:
                    return selected_action
            else:
                print("Invalid choice, please select a valid action.")


    def handle_blocks(self, action):
        if not action.blockable_by:
            return

        for player in self.players:
            if player != action.player and not player.is_eliminated:
                print(f"{player.name}, do you want to block this action? (yes/no)")
                decision = input().strip().lower()
                if decision == 'yes':
                    # Assuming a simplified block logic where the block is always successful
                    print(f"{player.name} has blocked the action!")
                    return True
        return False


    def handle_challenges(self, action):
        for player in self.players:
            if player != action.player and not player.is_eliminated:
                print(f"{player.name}, do you want to challenge this action? (yes/no)")
                decision = input().strip().lower()
                if decision == 'yes':
                    # Implement the challenge logic
                    print(f"{player.name} has challenged the action!")
                    if action.player.has_card(action.__class__.__name__):
                        print(f"Challenge failed. {action.player.name} has the {action.__class__.__name__}.")
                        # Handle the failure of the challenge
                    else:
                        print(f"Challenge succeeded. {action.player.name} does not have the {action.__class__.__name__}.")
                        # Handle the success of the challenge
                    return True
        return False
    
    def choose_target(self, acting_player):
        print("Choose a target for your action:")
        potential_targets = [p for p in self.players if p != acting_player and not p.is_eliminated]
        for i, player in enumerate(potential_targets, 1):
            print(f"{i}. {player.name}")

        while True:
            choice = input()
            if choice.isdigit() and 0 < int(choice) <= len(potential_targets):
                return potential_targets[int(choice) - 1]
            print("Invalid choice, please select a valid player.")





    def check_game_over(self):
        # Determine if the game is over and update self.game_over accordingly
        active_players = [p for p in self.players if not p.is_eliminated()]
        if len(active_players) == 1:
            self.game_over = True
            print(f"Game over! {active_players[0]} wins!")

if __name__ == "__main__":
    game = Game(num_players=4)
    game.run()


# class Game:
#     def __init__(self, players, deck):
#         self.players = players
#         self.deck = deck
#         self.current_player_index = 0
#         self.game_over = False

#     def start(self):
#         while not self.game_over:
#             current_player = self.players[self.current_player_index]
#             if not current_player.is_eliminated:
#                 self.execute_turn(current_player)
#             self.current_player_index = (self.current_player_index + 1) % len(self.players)
#             self.check_game_over()

#     def execute_turn(self, player):
#         print(f"\n{player.name}'s turn")
#         available_actions = self.get_available_actions(player)
#         chosen_action = self.choose_action(player, available_actions)
#         self.perform_action(chosen_action, player)

#     def get_available_actions(self, player):
#         # This would return a list of possible actions the player can perform
#         return [Income(player), ForeignAid(player), Coup(self, player, None)]  # Simplified example

#     def choose_action(self, player, available_actions):
#         # Here you would implement how a player chooses an action, possibly showing a menu
#         print(f"Available actions for {player.name}:")
#         for i, action in enumerate(available_actions, 1):
#             print(f"{i}. {action.__class__.__name__}")
#         choice = int(input("Choose an action: ")) - 1
#         return available_actions[choice]

#     def perform_action(self, action, player):
#         # Perform the chosen action and handle blocks and challenges
#         print(f"{player.name} has chosen to {action.__class__.__name__}")
#         action.perform_action()

#         # Check for reactions from other players (blocks or challenges)
#         for opponent in self.players:
#             if opponent != player and not opponent.is_eliminated:
#                 self.handle_reactions(action, opponent)

#     def handle_reactions(self, action, opponent):
#         # Placeholder for handling blocks and challenges from other players
#         pass

#     def check_game_over(self):
#         # Check if the game is over and set self.game_over appropriately
#         if len([player for player in self.players if not player.is_eliminated]) <= 1:
#             self.game_over = True
