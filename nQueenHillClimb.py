import random

def generate_board(n):
    return [random.randint(0, n - 1) for _ in range(n)]

def calculate_conflicts(board):
    conflicts = 0
    n = len(board)
    for i in range(n):
        for j in range(i + 1, n):
            if board[i] == board[j] or abs(board[i] - board[j]) == abs(i - j):
                conflicts += 1
    return conflicts

def get_best_neighbor(board):
    n = len(board)
    current_conflicts = calculate_conflicts(board)
    best_board = list(board)
    best_conflicts = current_conflicts

    for col in range(n):
        original_row = board[col]
        for row in range(n):
            if row == original_row:
                continue
            new_board = list(board)
            new_board[col] = row
            new_conflicts = calculate_conflicts(new_board)
            if new_conflicts < best_conflicts:
                best_conflicts = new_conflicts
                best_board = new_board

    return best_board, best_conflicts

def hill_climb(n, max_restarts=1000):
    for _ in range(max_restarts):
        board = generate_board(n)
        conflicts = calculate_conflicts(board)
        while True:
            next_board, next_conflicts = get_best_neighbor(board)
            if next_conflicts == 0:
                return next_board
            if next_conflicts >= conflicts:
                break
            board, conflicts = next_board, next_conflicts
    return None

def print_board(board):
    n = len(board)
    for row in range(n):
        line = ""
        for col in range(n):
            line += "Q " if board[col] == row else ". "
        print(line)

if __name__ == "__main__":
    N = 8
    solution = hill_climb(N)
    if solution:
        print_board(solution)
    else:
        print("No solution found.")
