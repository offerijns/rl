import math
import string

from util import cls
from hexboard import HexBoard
from minimax import Minimax
from evaluate import Evaluate
import time 

char_to_row_idx = { char: i for i, char in enumerate(string.ascii_lowercase) }

class HexGame:
    """This instance is responsible for running a single game."""

    def __init__(self, size, depth, time_limit, eval_method, disable_tt = False):
        """Creates a new HexGame using the provided boardsize, search depth for dijkstra and evaluation method"""
        self.board_size = size
        self.search_depth = depth
        self.minimax = Minimax(size, depth, time_limit, Evaluate(eval_method), disable_tt=disable_tt)

    def run_interactively(self, board):
        """Runs the game interactively, this starts a while loop that will only stop once the game is won or a draw is detected"""
        while not board.game_over():
            print("Waiting for CPU move...")
            move = self.minimax.get_next_move(board, HexBoard.RED)
            board = board.make_move(move, HexBoard.RED)
            board.print()
            print('\n')

            if board.game_over():
                break

            while True:
                move = input("Your move: ")

                if len(move) == 2:
                    x, y = move
                    if (x in char_to_row_idx and y.isdigit):
                        if board.is_empty((char_to_row_idx[x], int(y))):
                            break

            board = board.make_move((char_to_row_idx[x], int(y)), HexBoard.BLUE)

        if board.check_win(HexBoard.RED):
            print('The AI won.')
        else:
            print('You won.')
