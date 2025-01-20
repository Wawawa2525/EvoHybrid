import math
import random
import numpy as np

BLACK = 1
WHITE = 2

board = [
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 1, 2, 0, 0],
    [0, 0, 2, 1, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
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
            nx += dx
            ny += dy
            found_opponent = True

        if found_opponent and 0 <= nx < len(board[0]) and 0 <= ny < len(board) and board[ny][nx] == stone:
            return True

    return False

def get_valid_moves(board, stone):
    valid_moves = []
    for y in range(len(board)):
        for x in range(len(board[0])):
            if can_place_x_y(board, stone, x, y):
                valid_moves.append((x, y))
    return valid_moves

def make_move(board, stone, x, y):
    opponent = 3 - stone
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    board[y][x] = stone
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        tiles_to_flip = []

        while 0 <= nx < len(board[0]) and 0 <= ny < len(board) and board[ny][nx] == opponent:
            tiles_to_flip.append((nx, ny))
            nx += dx
            ny += dy

        if 0 <= nx < len(board[0]) and 0 <= ny < len(board) and board[ny][nx] == stone:
            for fx, fy in tiles_to_flip:
                board[fy][fx] = stone

# Neural Network-based AI
class NeuralNetwork:
    def __init__(self, input_size, hidden_size, output_size):
        self.weights_input_hidden = np.random.randn(input_size, hidden_size)
        self.weights_hidden_output = np.random.randn(hidden_size, output_size)

    def forward(self, inputs):
        hidden = np.dot(inputs, self.weights_input_hidden)
        hidden = self.sigmoid(hidden)
        output = np.dot(hidden, self.weights_hidden_output)
        return self.sigmoid(output)

    def sigmoid(self, x):
        return 1 / (1 + np.exp(-x))

# Genetic Algorithm-based Optimization
class GeneticAlgorithm:
    def __init__(self, population_size, mutation_rate):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.population = [NeuralNetwork(36, 18, 1) for _ in range(population_size)]

    def mutate(self, network):
        for layer in [network.weights_input_hidden, network.weights_hidden_output]:
            if random.random() < self.mutation_rate:
                layer += np.random.normal(0, 0.1, layer.shape)

    def crossover(self, parent1, parent2):
        child = NeuralNetwork(36, 18, 1)
        child.weights_input_hidden = (parent1.weights_input_hidden + parent2.weights_input_hidden) / 2
        child.weights_hidden_output = (parent1.weights_hidden_output + parent2.weights_hidden_output) / 2
        return child

    def select(self, fitness_scores):
        total_fitness = sum(fitness_scores)
        probabilities = [score / total_fitness for score in fitness_scores]
        return np.random.choice(self.population, p=probabilities)

    def evolve(self, fitness_scores):
        new_population = []
        for _ in range(self.population_size):
            parent1 = self.select(fitness_scores)
            parent2 = self.select(fitness_scores)
            child = self.crossover(parent1, parent2)
            self.mutate(child)
            new_population.append(child)
        self.population = new_population

class PandaAI:
    def __init__(self):
        self.ga = GeneticAlgorithm(10, 0.1)

    def face(self):
        return "🐼"

    def place(self, board, stone):
        valid_moves = get_valid_moves(board, stone)
        if not valid_moves:
            return None

        board_flat = np.array(board).flatten()
        fitness_scores = []

        for network in self.ga.population:
            scores = []
            for x, y in valid_moves:
                test_board = [row[:] for row in board]
                make_move(test_board, stone, x, y)
                board_flat_test = np.array(test_board).flatten()
                scores.append(network.forward(board_flat_test))
            fitness_scores.append(max(scores))

        self.ga.evolve(fitness_scores)
        best_move = valid_moves[np.argmax(fitness_scores)]
        return best_move
