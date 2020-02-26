import argparse
import sys
from tqdm import tqdm
from trueskill import Rating, rate_1vs1
import time
from multiprocessing import Pool, freeze_support
from copy import deepcopy

from hexboard import HexBoard
from minimax import Minimax
from evaluate import Evaluate
from game import HexGame

def save_result(start_time, data):
    """Saves the provided data to the disk using the provided start_time as .csv"""
    with open('results/' + start_time + '.csv','a') as fd:
        fd.write(','.join(map(str, data)) + '\n')

def play_game(game_input):
    """Plays a series of games according to the provided game input object which packs all the settings into one object"""
    process_id, board_size, game_cnt, start_time, p1, p2, disable_tt = game_input

    r1 = Rating()
    r2 = Rating()
    r1_col, r2_col = HexBoard.RED, HexBoard.BLUE
    r1_first = True

    text = "Processor %d" % (process_id)

    for game_id in tqdm(range(1, game_cnt + 1), desc=text, position=process_id):
        m1, m2 = Minimax(board_size, p1['depth'], p1['time_limit'], Evaluate(p1['eval']), False, disable_tt=disable_tt), Minimax(board_size, p2['depth'], p2['time_limit'], Evaluate(p2['eval']), False, disable_tt=disable_tt)
        board = HexBoard(board_size)

        r1_first = True if not r1_first else False
        r1_turn = True if r1_first else False

        first_color = r1_col if r1_first else r2_col
        second_color =  r2_col if r1_first else r1_col
        
        while not board.game_over():
            move = (m1 if r1_turn else m2).get_next_move(board, r1_col if r1_turn else r2_col)
            board.place(move, r1_col if r1_turn else r2_col)
            r1_turn = False if r1_turn else True

        if board.check_draw():
            r1, r2 = rate_1vs1(r1, r2, drawn=True)
        elif board.check_win(r1_col):
            r1, r2 = rate_1vs1(r1, r2, drawn=False)
        elif board.check_win(r2_col):
            r2, r1 = rate_1vs1(r2, r1, drawn=False)
        
        save_result(start_time, (p1['depth'], p1['time_limit'], p1['eval'], p2['depth'], p2['time_limit'], p2['eval'], game_id, r1.mu, r1.sigma, r2.mu, r2.sigma))
        
    print(r1)
    print(r2)

def run_trueskill(args):
    """Surprise, starts a trueskill comparison for each of the possible permutations of the input players"""
    freeze_support() # for Windows support

    board_size = 4
    game_cnt = 100
    # players = [{ 'depth': 3, 'eval': 'random' }, { 'depth': 3, 'eval': 'Dijkstra' }, { 'depth': 4, 'eval': 'Dijkstra' }]
    players = [{ 'depth': 3, 'time_limit': None, 'eval': 'random' }, { 'depth': None, 'time_limit': 0.1, 'eval': 'Dijkstra' }]

    player_permutations = []
    for i in range(len(players)):
        for j in range(i + 1, len(players)):
            player_permutations.append((players[i], players[j]))

    start_time = str(int(time.time()))
    save_result(start_time, ('p1_depth', 'p1_time_limit', 'p1_eval', 'p2_depth', 'p2_time_limit', 'p2_eval', 'game_id', 'r1_mu', 'r1_sigma', 'r2_mu', 'r2_sigma'))

    game_inputs = [(process_id, board_size, game_cnt, start_time, p1, p2, args.disable_tt) for process_id, (p1, p2) in enumerate(player_permutations)]

    pool = Pool(len(game_inputs))
    pool.map(play_game, game_inputs)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Minimax for Hex")
    parser.add_argument('--trueskill', action='store_true', help='If added, evaluate using TrueSkill')
    parser.add_argument('--disable-tt', action='store_true', help='If added, disables the transposition table')
    parser.add_argument('--size', type=int, default=4, help='Set the board size')
    parser.add_argument('--depth', type=int, default=4, help='Set the search depth')
    parser.add_argument('--eval', choices=['Dijkstra', 'random'], default='Dijkstra', help='Choose the evaluation method')
    args = parser.parse_args(sys.argv[1:])

    game = HexGame(args.size, args.depth, args.eval, args.disable_tt)
    board = HexBoard(args.size)

    if args.trueskill:
        run_trueskill(args)
    else:
        game.run_interactively(board)
