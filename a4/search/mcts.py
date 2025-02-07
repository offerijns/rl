import logging
import random
import math
import time
from collections import defaultdict
from operator import attrgetter

from util import cls
from util.hexboard import HexBoard
from search import HexSearchMethod
from search.debug import log_tree
from search import selection_rules

logger = logging.getLogger(__name__)

class MCTS(HexSearchMethod):
    """This object houses all the code necessary for the MCTS implementation"""

    def __init__(self, num_iterations, time_limit = None, Cp = 0.4, live_play=True, rave_k=-1, debug=False):
        """Initializes MCTS search object with the provided settings"""
        self.num_iterations = num_iterations
        self.time_limit = time_limit
        self.Cp = Cp
        self.live_play = live_play
        self.rave_k = rave_k
        self.debug = debug
        
    def get_next_move(self, board, color):
        """Returns the best next move using the MCTS search algorithm. This will run untill either the time limit or 
        the amount of allowed iterations has passed"""
        start_time = time.time()
        self.root = MCTSNode(board.copy(), parent=None, player=color, turn=color, rave_k=self.rave_k)

        # Run the main MCTS loop num_iterations times
        i = 0
        if self.num_iterations:
            for _ in range(self.num_iterations):
                self.run_iteration(i)
                i += 1
        else:
            while (time.time() - start_time) < self.time_limit:
                self.run_iteration(i)
                i += 1
                
        if self.live_play:
            elapsed_time = time.time() - start_time
            cls()
            print("Generation of this next move took %.2f seconds, ran %d iterations." % (elapsed_time, i))

        if self.debug: log_tree(self.root)

        next_board = self.root.child_with_most_visits(self.num_iterations).board
        return HexBoard.get_move_between_boards(self.root.board, next_board)
    
    def run_iteration(self, iteration_idx):
        """Runs a single iteration of the MCTS search algorithm"""
        node = self.select_and_expand(iteration_idx)
        reward = node.simulate()
        node.backpropagate(reward, node.player)

    def select_and_expand(self, iteration_idx):
        """Expands child nodes and handles UCT selection"""
        current_node = self.root
        winner = current_node.board.get_winner()
        while winner is None:
            if len(current_node.untried_moves) > 0:
                return current_node.expand()
            else:
                current_node = current_node.best_child(self.Cp) # UCT select
            winner = current_node.board.get_winner()
        return current_node

    def __str__(self):
        """"Simple toString implementation, useful for debugging only"""
        return 'MCTS(%d, %.2fs, %.2f, %d)' % (
            self.num_iterations if self.num_iterations is not None else 0,
            self.time_limit if self.time_limit is not None else 0,
            self.Cp,
            self.rave_k
        )
        
class MCTSNode:
    """A single MCTS node in the search tree"""

    def __init__(self, board, player, parent=None, turn=None, rave_k=0.0):
        """Creates a single node using the provided arguments"""
        self.board = board
        self.player = player
        self.parent = parent
        self.turn = turn
        
        self.children = []
        self.untried_moves = self.board.get_possible_moves()

        self.simulated_moves_by_player = { 1: [], 2: [] }

        self.num_visits, self.num_amaf_visits = 0, 0
        self.reward, self.amaf_reward = 0, 0

        self.rave_k = rave_k

    def expand(self):
        """Expands one of the possible child moves"""
        move = self.untried_moves.pop() 
        next_board = self.board.make_move(move, self.player)
        child_node = MCTSNode(next_board, parent=self, player=self.player, turn=HexBoard.get_opposite_color(self.turn), rave_k=self.rave_k)
        self.children.append(child_node)
        return child_node
    
    def simulate(self):
        """Runs the game simulation playing random moves untill a terminal condition (win/loss/draw) is found"""
        if self.rave_k > 0.0: self.simulated_moves_by_player = { 1: [], 2: [] }

        current_board = self.board.copy()
        all_moves = current_board.get_possible_moves()
        random.shuffle(all_moves)

        current_turn = self.player
        winner = current_board.get_winner()

        while winner is None:
            move = all_moves.pop()

            if self.rave_k > 0:
                self.simulated_moves_by_player[current_turn].append(move) # Store a list of all simulated moves

            current_board.place(move, current_turn)
            current_turn = HexBoard.RED if current_turn == HexBoard.BLUE else HexBoard.BLUE
            winner = current_board.get_winner()

        return HexBoard.get_reward(self.player, winner)

    def backpropagate(self, reward, turn=None):
        """Propagates the reward back through the tree. If we are using RAVE also tries to update siblings"""
        self.num_visits += 1
        self.reward += reward

        if self.parent is not None:
            if self.rave_k > 0:
                # Run All-Moves-As-First
                simulated_boards = [self.board.make_move(move, self.turn).hash_code() for move in self.simulated_moves_by_player[self.turn]]

                for child in self.children:
                    if child.board.hash_code() in simulated_boards:
                        child.num_amaf_visits += 1
                        child.amaf_reward += reward

            # Backpropagate further up
            self.parent.backpropagate(reward, HexBoard.get_opposite_color(turn))
    
    def child_with_most_visits(self, num_iterations):
        """Returns the child with the visits, since that should be the best action, according to the book"""
        # return self.best_child(0.0)
        return max(self.children, key=attrgetter('num_visits'))

    def best_child(self, Cp):
        """Returns the best child using the provided Cp score. Cp of zero just exploitation, thus returning the best found so far"""
        ln_N = selection_rules.log_n(self.num_visits)

        if self.rave_k > 0:
            return max(self.children, key=lambda child: selection_rules.rave_score(child, self.rave_k, Cp, ln_N))
        else:
            return max(self.children, key=lambda child: selection_rules.uct_score(child.reward, child.num_visits, Cp, ln_N))