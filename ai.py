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

def dynamic_depth(empty_cells):
    if empty_cells > 20:
        return 2
    elif empty_cells > 10:
        return 3
    else:
        return 5

def monte_carlo_simulation(board, stone, x, y, simulations=30):
    opponent = 3 - stone
    win_count = 0

    for _ in range(simulations):
        simulated_board = make_move(board, stone, x, y)
        current_player = opponent

        while can_place(simulated_board, stone) or can_place(simulated_board, opponent):
            if can_place(simulated_board, current_player):
                possible_moves = [
                    (i, j) for j in range(len(board)) for i in range(len(board[0]))
                    if can_place_x_y(simulated_board, current_player, i, j)
                ]
                move = random.choice(possible_moves)
                simulated_board = make_move(simulated_board, current_player, move[0], move[1])
            current_player = 3 - current_player

        final_score = sum(row.count(stone) for row in simulated_board)
        opponent_score = sum(row.count(opponent) for row in simulated_board)
        if final_score > opponent_score:
            win_count += 1

    return win_count / simulations

def best_place_with_monte_carlo(board, stone):
    best_score = -float('inf')
    best_move = None

    for y in range(len(board)):
        for x in range(len(board[0])):
            if can_place_x_y(board, stone, x, y):
                win_rate = monte_carlo_simulation(board, stone, x, y)
                if win_rate > best_score:
                    best_score = win_rate
                    best_move = (x, y)

    return best_move

def count_stable_stones(board, stone):
    stable_count = 0
    # 確定石ロジックをここに追加
    return stable_count

def evaluate_with_stable_stones(board, stone):
    stable_stones = count_stable_stones(board, stone)
    return evaluate_board(board, stone) + stable_stones * 50

class HybridAI(object):

    def face(self):
        return "✨"

    def place(self, board, stone):
        valid_moves = [(x, y) for y in range(len(board)) for x in range(len(board[0])) if can_place_x_y(board, stone, x, y)]

        if not valid_moves:
            return None

        empty_cells = sum(row.count(0) for row in board)

        if empty_cells <= 10:  # 終盤戦略
            best_score = -float('inf')
            best_move = None
            for x, y in valid_moves:
                simulated_board = make_move(board, stone, x, y)
                score = evaluate_with_stable_stones(simulated_board, stone)
                if score > best_score:
                    best_score = score
                    best_move = (x, y)
            return best_move

        return best_place_with_monte_carlo(board, stone)
