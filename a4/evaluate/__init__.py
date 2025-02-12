import math
from functools import lru_cache

from util.hexboard import HexBoard

class HexEvalMethod:

    def __init(self, eval_method):
        self.eval_method = eval_method

    def evaluate_board(board, color):
        raise NotImplementedError
    
    @lru_cache(maxsize=8)
    def distance_to(self, color_b, opposite_color):
        """Returns the distance between the two provided colors, this is the vertex cost for Dijkstra"""
        if color_b == opposite_color:
            return math.inf
        elif color_b == HexBoard.EMPTY:
            return 1
        else:
            return 0

    def evaluate_board(self, board, color):
        winner = board.get_winner()
        if winner is not None: return HexBoard.get_reward(color, winner) * 1000
        
        player_sp = self.find_shortest_path_to_border(board, color)
        opponent_sp = self.find_shortest_path_to_border(board, HexBoard.get_opposite_color(color))

        if player_sp == math.inf: player_sp = 0
        if opponent_sp == math.inf: opponent_sp = 0

        return -(player_sp - opponent_sp)

    def get_score(self, board, from_coord, target_coords, color, opposite_color):
        raise NotImplementedError

    def find_shortest_path_to_border(self, board, color):
        """Returns the length of the shortest possible path to the border for the specified color"""
        source_coords = board.source_coords[color]
        target_coords = board.target_coords[color]
        opposite_color = HexBoard.get_opposite_color(color)
        
        min_score = board.size**2

        for from_coord in source_coords:
            if board.get_color(from_coord) == opposite_color:
                continue

            score = self.get_score(board, from_coord, target_coords, color, opposite_color)

            if score < min_score:
                min_score = score

        return min_score
