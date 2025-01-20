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

def evaluate_board(board, stone):
    opponent = 3 - stone
    score = 0

    weight_map = [
        [100, -20, 10, 10, -20, 100],
        [-20, -50, -2, -2, -50, -20],
        [10, -2, 1, 1, -2, 10],
        [10, -2, 1, 1, -2, 10],
        [-20, -50, -2, -2, -50, -20],
        [100, -20, 10, 10, -20, 100]
    ]

    for y in range(len(board)):
        for x in range(len(board[0])):
            if board[y][x] == stone:
                score += weight_map[y][x]
            elif board[y][x] == opponent:
                score -= weight_map[y][x]

    return score

def dynamic_evaluate_board(board, stone, stage):
    early_weight = [
        [100, -20, 10, 10, -20, 100],
        [-20, -50, -2, -2, -50, -20],
        [10, -2, 1, 1, -2, 10],
        [10, -2, 1, 1, -2, 10],
        [-20, -50, -2, -2, -50, -20],
        [100, -20, 10, 10, -20, 100],
    ]
    late_weight = [
        [100, 80, 50, 50, 80, 100],
        [80, 30, 20, 20, 30, 80],
        [50, 20, 10, 10, 20, 50],
        [50, 20, 10, 10, 20, 50],
        [80, 30, 20, 20, 30, 80],
        [100, 80, 50, 50, 80, 100],
    ]

    weight = early_weight if stage == "early" else late_weight
    score = 0

    for y in range(len(board)):
        for x in range(len(board[0])):
            if board[y][x] == stone:
                score += weight[y][x]

    return score

def apply_move(board, stone, x, y):
    new_board = [row[:] for row in board]
    new_board[y][x] = stone

    opponent = 3 - stone
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        stones_to_flip = []

        while 0 <= nx < len(new_board[0]) and 0 <= ny < len(new_board) and new_board[ny][nx] == opponent:
            stones_to_flip.append((nx, ny))
            nx += dx
            ny += dy

        if stones_to_flip and 0 <= nx < len(new_board[0]) and 0 <= ny < len(new_board) and new_board[ny][nx] == stone:
            for flip_x, flip_y in stones_to_flip:
                new_board[flip_y][flip_x] = stone

    return new_board

def get_valid_moves(board, stone):
    valid_moves = []
    for y in range(len(board)):
        for x in range(len(board[0])):
            if can_place_x_y(board, stone, x, y):
                valid_moves.append((x, y))
    return valid_moves

def can_place_x_y(board, stone, x, y):
    if board[y][x] != 0:
        return False

    opponent = 3 - stone
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        found_opponent = False

        while 0 <= nx < len(board[0]) and 0 <= ny < len(board) and board[ny][nx] == opponent:
            nx += dx
            ny += dy
            found_opponent = True

        if found_opponent and 0 <= nx < len(board[0]) and 0 <= ny < len(board) and board[ny][nx] == stone:
            return True

    return False

def dynamic_evaluate_board(board, stone, stage):
    early_weight = [
        [100, -20, 10, 10, -20, 100],
        [-20, -50, -2, -2, -50, -20],
        [10, -2, 0, 0, -2, 10],
        [10, -2, 0, 0, -2, 10],
        [-20, -50, -2, -2, -50, -20],
        [100, -20, 10, 10, -20, 100],
    ]
    late_weight = [
        [100, 80, 50, 50, 80, 100],
        [80, 30, 20, 20, 30, 80],
        [50, 20, 10, 10, 20, 50],
        [50, 20, 10, 10, 20, 50],
        [80, 30, 20, 20, 30, 80],
        [100, 80, 50, 50, 80, 100],
    ]

    weight = early_weight if stage == "early" else late_weight
    score = 0

    for y in range(len(board)):
        for x in range(len(board[0])):
            if board[y][x] == stone:
                score += weight[y][x]

    return score

def dynamic_depth(empty_cells):
    if empty_cells > 20:
        return 3
    elif empty_cells > 10:
        return 5
    else:
        return 7

def minimax(board, stone, depth, maximizing_player, alpha=-math.inf, beta=math.inf):
    valid_moves = get_valid_moves(board, stone)

    if depth == 0 or not valid_moves:
        return dynamic_evaluate_board(board, stone, "late")

    if maximizing_player:
        max_eval = -math.inf
        for x, y in valid_moves:
            new_board = apply_move(board, stone, x, y)
            eval = minimax(new_board, 3 - stone, depth - 1, False, alpha, beta)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = math.inf
        for x, y in valid_moves:
            new_board = apply_move(board, stone, x, y)
            eval = minimax(new_board, 3 - stone, depth - 1, True, alpha, beta)
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval

def count_stable_stones(board, stone):
    stable_count = 0
    # 確定石ロジックを実装
    return stable_count

def evaluate_with_stable_stones(board, stone):
    stable_stones = count_stable_stones(board, stone)
    return dynamic_evaluate_board(board, stone, "late") + stable_stones * 50

class HybridAI:

    def face(self):
        return "✨"

    def place(self, board, stone):
        valid_moves = get_valid_moves(board, stone)

        if not valid_moves:
            return None

        empty_cells = sum(row.count(0) for row in board)

        if empty_cells > 20:
            stage = "early"
        elif empty_cells > 10:
            stage = "mid"
        else:
            stage = "late"

        best_score = -math.inf
        best_move = None

        for x, y in valid_moves:
            new_board = apply_move(board, stone, x, y)
            if stage == "late":
                score = minimax(new_board, 3 - stone, depth=dynamic_depth(empty_cells), maximizing_player=False)
            else:
                score = evaluate_with_stable_stones(new_board, stone)

            if score > best_score:
                best_score = score
                best_move = (x, y)

        return best_move
