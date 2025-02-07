import math
import string
import time 

from util import cls
from util.hexboard import HexBoard

from search.minimax import Minimax
from search.mcts import MCTS

from evaluate.dijkstra import Dijkstra
from evaluate.astar import AStar
from evaluate.random import RandomEval

char_to_row_idx = { char: i for i, char in enumerate(string.ascii_lowercase) }

class HexGame:
    """This instance is responsible for running a single game."""

    def __init__(self, args):
        """Creates a new HexGame using the provided boardsize, search depth for dijkstra and evaluation method"""
        self.board_size = args.size

        if args.eval == 'Dijkstra':
            eval_class = Dijkstra()
        elif args.eval == 'AStar':
            eval_class = AStar()
        elif args.eval == 'random':
            eval_class = RandomEval()

        if args.search == 'minimax':
            self.search = Minimax(args.depth, args.time_limit, eval_class, disable_tt=args.disable_tt)
        elif args.search == 'mcts':
            self.search = MCTS(args.num_iterations, args.time_limit, args.cp, True, args.rave_k)

    def run_interactively(self, board):
        """Runs the game interactively, this starts a while loop that will only stop once the game is won or a draw is detected"""
        winner = board.get_winner()
        while winner is None:
            print("Waiting for CPU move...")
            move = self.search.get_next_move(board, HexBoard.RED)
            board = board.make_move(move, HexBoard.RED)
            board.print()
            print('\n')

            if board.get_winner() is not None:
                break

            while True:
                move = input("Your move: ")

                if len(move) == 2:
                    x, y = move
                    if (x in char_to_row_idx and y.isdigit):
                        if board.is_empty((char_to_row_idx[x], int(y))):
                            break

            board = board.make_move((char_to_row_idx[x], int(y)), HexBoard.BLUE)
            winner = board.get_winner()

        if winner == HexBoard.RED:
            print('The AI won.')
        else:
            print('You won.')
