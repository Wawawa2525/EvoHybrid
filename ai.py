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

def get_valid_moves(board, stone):
    return [(x, y) for y in range(len(board)) for x in range(len(board[0])) if can_place_x_y(board, stone, x, y)]

def apply_move(board, stone, x, y):
    new_board = [row[:] for row in board]
    new_board[y][x] = stone
    opponent = 3 - stone
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        stones_to_flip = []
        while 0 <= nx < len(board[0]) and 0 <= ny < len(board) and new_board[ny][nx] == opponent:
            stones_to_flip.append((nx, ny))
            nx += dx
            ny += dy
        if stones_to_flip and 0 <= nx < len(board[0]) and 0 <= ny < len(board) and new_board[ny][nx] == stone:
            for fx, fy in stones_to_flip:
                new_board[fy][fx] = stone
    return new_board

def evaluate_board(board, stone, stage):
    weights = {
        "early": [[100, -20, 10, 10, -20, 100], ...],
        "mid": [[...]],  # 中盤の評価重みを定義
        "late": [[...]]  # 終盤の評価重みを定義
    }
    score = sum(weights[stage][y][x] for y in range(len(board)) for x in range(len(board[0])) if board[y][x] == stone)
    score += evaluate_opponent_moves(board, stone)
    return score

def dynamic_depth(empty_cells):
    if empty_cells > 20:
        return 3
    elif empty_cells > 10:
        return 5
    else:
        return 7

class HybridAI:
    def face(self):
        return "✨"

    def place(self, board, stone):
        valid_moves = get_valid_moves(board, stone)
        if not valid_moves:
            return None
        empty_cells = sum(row.count(0) for row in board)
        stage = "early" if empty_cells > 20 else "mid" if empty_cells > 10 else "late"
        depth = dynamic_depth(empty_cells)
        best_score = -math.inf
        best_move = None
        for x, y in valid_moves:
            new_board = apply_move(board, stone, x, y)
            if stage == "late":
                score = minimax(new_board, 3 - stone, depth, False)
            else:
                score = evaluate_board(new_board, stone, stage)
            if score > best_score:
                best_score = score
                best_move = (x, y)
        return best_move
