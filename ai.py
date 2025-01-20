import math
import random
import copy
from concurrent.futures import ThreadPoolExecutor

BLACK = 1
WHITE = 2

board = [
        [0,0,0,0,0,0],
        [0,0,0,0,0,0],
        [0,0,1,2,0,0],
        [0,0,2,1,0,0],
        [0,0,0,0,0,0],
        [0,0,0,0,0,0],
]

def can_place_x_y(board, stone, x, y):
    """
    石を置けるかどうかを調べる関数。
    board: 2次元配列のオセロボード
    x, y: 石を置きたい座標 (0-indexed)
    stone: 現在のプレイヤーの石 (1: 黒, 2: 白)
    return: 置けるなら True, 置けないなら False
    """
    if board[y][x] != 0:
        return False  # 既に石がある場合は置けない

    opponent = 3 - stone  # 相手の石 (1なら2、2なら1)
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        found_opponent = False

        while 0 <= nx < len(board[0]) and 0 <= ny < len(board) and board[ny][nx] == opponent:
            nx += dx
            ny += dy
            found_opponent = True

        if found_opponent and 0 <= nx < len(board[0]) and 0 <= ny < len(board) and board[ny][nx] == stone:
            return True  # 石を置ける条件を満たす

    return False

def can_place(board, stone):
    """
    石を置ける場所を調べる関数。
    board: 2次元配列のオセロボード
    stone: 現在のプレイヤーの石 (1: 黒, 2: 白)
    """
    for y in range(len(board)):
        for x in range(len(board[0])):
            if can_place_x_y(board, stone, x, y):
                return True
    return False

def random_place(board, stone):
    """
    石をランダムに置く関数。
    board: 2次元配列のオセロボード
    stone: 現在のプレイヤーの石 (1: 黒, 2: 白)
    """
    while True:
        x = random.randint(0, len(board[0]) - 1)
        y = random.randint(0, len(board) - 1)
        if can_place_x_y(board, stone, x, y):
            return x, y


# 評価表
EARLY_EVAL_TABLE = [
    [200, -100, 50, 50, -100, 200],
    [-100, -200, -10, -10, -200, -100],
    [50, -10, 0, 0, -10, 50],
    [50, -10, 0, 0, -10, 50],
    [-100, -200, -10, -10, -200, -100],
    [200, -100, 50, 50, -100, 200],
]

MID_EVAL_TABLE = [
    [100, -20, 10, 10, -20, 100],
    [-20, -50, 0, 0, -50, -20],
    [10, 0, 5, 5, 0, 10],
    [10, 0, 5, 5, 0, 10],
    [-20, -50, 0, 0, -50, -20],
    [100, -20, 10, 10, -20, 100],
]

LATE_EVAL_TABLE = [
    [100, -20, 10, 10, -20, 100],
    [-20, -50, 20, 20, -50, -20],
    [10, 20, 50, 50, 20, 10],
    [10, 20, 50, 50, 20, 10],
    [-20, -50, 20, 20, -50, -20],
    [100, -20, 10, 10, -20, 100],
]

def can_place_x_y(board, stone, x, y):
    if board[y][x] != 0:
        return False

    opponent = 3 - stone
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        found_opponent = False

        while 0 <= nx < len(board[0]) and 0 <= ny < len(board) and board[ny][nx] == opponent:
            found_opponent = True
            nx += dx
            ny += dy

        if found_opponent and 0 <= nx < len(board[0]) and 0 <= ny < len(board) and board[ny][nx] == stone:
            return True

    return False

def can_place(board, stone):
    for y in range(len(board)):
        for x in range(len(board[0])):
            if can_place_x_y(board, stone, x, y):
                return True
    return False

def make_move(board, stone, x, y):
    new_board = [row[:] for row in board]
    opponent = 3 - stone
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    new_board[y][x] = stone

    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        flips = []

        while 0 <= nx < len(board[0]) and 0 <= ny < len(board) and new_board[ny][nx] == opponent:
            flips.append((nx, ny))
            nx += dx
            ny += dy

        if 0 <= nx < len(board[0]) and 0 <= ny < len(board) and new_board[ny][nx] == stone:
            for fx, fy in flips:
                new_board[fy][fx] = stone

    return new_board

# 動的評価関数
def evaluate_board_with_table(board, stone, eval_table):
    score = 0
    for y in range(len(board)):
        for x in range(len(board[0])):
            if board[y][x] == stone:
                score += eval_table[y][x]
            elif board[y][x] == 3 - stone:
                score -= eval_table[y][x]
    return score

def evaluate_risk_move(board, stone, x, y):
    x_squares = [(0, 1), (1, 0), (1, 1), (0, 4), (1, 5), (1, 4),
                 (4, 0), (5, 1), (4, 1), (4, 5), (5, 4), (4, 4)]
    adjacent_to_corners = [(0, 2), (2, 0), (2, 5), (5, 2), 
                           (0, 3), (3, 0), (3, 5), (5, 3)]
    if (x, y) in x_squares:
        return -200
    elif (x, y) in adjacent_to_corners:
        return -100
    return 0

# 動的なシミュレーション数
def dynamic_simulation_count(total_stones):
    if total_stones < 20:
        return 5000
    elif total_stones < 50:
        return 3000
    else:
        return 1000

# 確定石のカウント
def count_stable_stones(board, stone):
    stable_count = 0
    # 確定石ロジックをここに実装
    return stable_count

# MCTSの改善
def improved_mcts_move(board, stone, simulations):
    moves = [(x, y) for y in range(len(board)) for x in range(len(board[0])) if can_place_x_y(board, stone, x, y)]
    if not moves:
        return None

    def simulate_move(move):
        scores = 0
        for _ in range(simulations // len(moves)):
            simulated_board = make_move(board, stone, move[0], move[1])
            current_stone = 3 - stone
            for _ in range(10):
                valid_moves = [(x, y) for y in range(len(board)) for x in range(len(board[0])) if can_place_x_y(simulated_board, current_stone, x, y)]
                if not valid_moves:
                    break
                random_move = random.choice(valid_moves)
                simulated_board = make_move(simulated_board, current_stone, random_move[0], random_move[1])
                current_stone = 3 - current_stone
            scores += evaluate_board_with_table(simulated_board, stone, MID_EVAL_TABLE)
        return scores

    move_scores = {move: simulate_move(move) + evaluate_risk_move(board, stone, move[0], move[1]) for move in moves}
    best_move = max(move_scores, key=move_scores.get)
    return best_move

# αβ探索
def alpha_beta(board, stone, depth, alpha, beta, maximizing):
    if depth == 0 or not can_place(board, stone):
        return evaluate_board_with_table(board, stone, LATE_EVAL_TABLE), None

    moves = [(x, y) for y in range(len(board)) for x in range(len(board[0])) if can_place_x_y(board, stone, x, y)]

    if maximizing:
        max_eval = -float('inf')
        best_move = None
        for x, y in moves:
            new_board = make_move(board, stone, x, y)
            eval_score, _ = alpha_beta(new_board, 3 - stone, depth - 1, alpha, beta, False)
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = (x, y)
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        min_eval = float('inf')
        best_move = None
        for x, y in moves:
            new_board = make_move(board, 3 - stone, x, y)
            eval_score, _ = alpha_beta(new_board, stone, depth - 1, alpha, beta, True)
            if eval_score < min_eval:
                min_eval = eval_score
                best_move = (x, y)
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        return min_eval, best_move

class HybridAI(object):

    def face(self):
        return "✨"

    def place(self, board, stone):
        valid_moves = [(x, y) for y in range(len(board)) for x in range(len(board[0])) if can_place_x_y(board, stone, x, y)]
        if not valid_moves:
            return None

        total_stones = sum(row.count(BLACK) + row.count(WHITE) for row in board)

        if total_stones < 20:  # 序盤
            _, best_move = alpha_beta(board, stone, depth=6, alpha=-float('inf'), beta=float('inf'), maximizing=True)
            return best_move
        elif total_stones < 50:  # 中盤
            simulations = dynamic_simulation_count(total_stones)
            return improved_mcts_move(board, stone, simulations)
        else:  # 終盤
            _, best_move = alpha_beta(board, stone, depth=10, alpha=-float('inf'), beta=float('inf'), maximizing=True)
            return best_move
