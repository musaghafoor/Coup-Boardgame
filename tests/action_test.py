
import unittest
from unittest.mock import MagicMock, patch
from actions.action_new import Income, ForeignAid, Coup, Tax, Assassinate, Steal, Exchange
from game.game_new import Game
from game.player_new import Player
from cards.deck import Deck
from cards.card import Card
from exceptions.game_exceptions import *

class ActionTest(unittest.TestCase):
    def setUp(self):
        self.deck = Deck()
        self.game = Game(self.deck)
        self.player1 = Player('Player 1')
        self.player2 = Player('Player 2')
        self.game.players = [self.player1, self.player2]
        self.card1 = Card('Duke')
        self.card2 = Card('Assassin')
        self.card3 = Card('Captain')
        self.card4 = Card('Ambassador')
        self.card5 = Card('Contessa')
        self.player1.hand = [self.card1, self.card2]
        self.player2.hand = [self.card3, self.card4]

    def test_income_action(self):
        action = Income(self.game, self.player1)
        action.perform_action()
        self.assertEqual(self.player1.coins, 3)

    def test_foreign_aid_action(self):
        action = ForeignAid(self.game, self.player1)
        action.perform_action()
        self.assertEqual(self.player1.coins, 4)

        self.player2.hand.append(self.card1)  # Duke for blocking
        with patch.object(Player, 'has_card', return_value=True):
            with self.assertRaises(GameException):
                action.perform_action()

    def test_coup_action(self):
        self.player1.coins = 7
        action = Coup(self.game, self.player1, self.player2)
        with patch.object(Player, 'lose_influence') as mock_lose_influence:
            action.perform_action()
            mock_lose_influence.assert_called_once()
        self.assertEqual(self.player1.coins, 0)

    def test_tax_action(self):
        action = Tax(self.game, self.player1)
        action.perform_action()
        self.assertEqual(self.player1.coins, 5)

    def test_assassinate_action(self):
        self.player1.coins = 3
        action = Assassinate(self.game, self.player1, self.player2)
        with patch.object(Player, 'lose_influence') as mock_lose_influence:
            action.perform_action()
            mock_lose_influence.assert_called_once()
        self.assertEqual(self.player1.coins, 0)

    def test_steal_action(self):
        self.player2.coins = 4
        action = Steal(self.game, self.player1, self.player2)
        action.perform_action()
        self.assertEqual(self.player1.coins, 4)
        self.assertEqual(self.player2.coins, 2)

    def test_exchange_action(self):
        self.deck.cards.extend([self.card1, self.card2, self.card3, self.card4, self.card5])
        action = Exchange(self.game, self.player1)
        with patch('builtins.input', side_effect=['1', '2']):
            action.perform_action()
        self.assertEqual(len(self.player1.hand), 2)

if __name__ == '__main__':
    unittest.main()
