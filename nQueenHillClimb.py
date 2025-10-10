import random

def generate_board(n):
   
    return [random.randint(0, n-1) for _ in range(n)]

def print_board(board):
    n = len(board)
    for row in range(n):
        line = ""
        for col in range(n):
            if board[col] == row:
                line += "Q "
            else:
                line += ". "
        print(line)
    print()

def get_attacking_pairs(board):
   
    n = len(board)
    attacks = 0
    for i in range(n):
        for j in range(i+1, n):
            if board[i] == board[j]:
                attacks += 1 
            elif abs(board[i] - board[j]) == abs(i - j):
                attacks += 1  
    return attacks

def get_neighbors(board):
    
    neighbors = []
    n = len(board)
    for col in range(n):
        for row in range(n):
            if board[col] != row:
                new_board = board.copy()
                new_board[col] = row
                neighbors.append(new_board)
    return neighbors

def hill_climbing(n, max_iterations=1000):
    current = generate_board(n)
    current_attacks = get_attacking_pairs(current)
    
    for i in range(max_iterations):
        neighbors = get_neighbors(current)
        neighbor_attacks = [get_attacking_pairs(nb) for nb in neighbors]
        
        min_attacks = min(neighbor_attacks)
        if min_attacks >= current_attacks:
            break
        
        current = neighbors[neighbor_attacks.index(min_attacks)]
        current_attacks = min_attacks
        
        if current_attacks == 0:

            break
    
    return current, current_attacks


n = 8
solution, attacks = hill_climbing(n)

print(f"Solution (0-based row for each column): {solution}")
print(f"Number of attacking pairs: {attacks}")
print_board(solution)
