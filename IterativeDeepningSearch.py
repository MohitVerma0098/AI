from collections import deque

# Goal state
goal_state = (1, 2, 3,
              4, 5, 6,
              7, 8, 0)

# Possible moves: Up, Down, Left, Right (index shifts)
moves = {
    'Up': -3,
    'Down': 3,
    'Left': -1,
    'Right': 1
}

def is_valid_move(blank_idx, move):
    if move == 'Left' and blank_idx % 3 == 0:
        return False
    if move == 'Right' and blank_idx % 3 == 2:
        return False
    if move == 'Up' and blank_idx < 3:
        return False
    if move == 'Down' and blank_idx > 5:
        return False
    return True

def move_blank(state, move):
    blank_idx = state.index(0)
    if not is_valid_move(blank_idx, move):
        return None
    swap_idx = blank_idx + moves[move]
    new_state = list(state)
    new_state[blank_idx], new_state[swap_idx] = new_state[swap_idx], new_state[blank_idx]
    return tuple(new_state)

def dfs(state, depth, limit, visited, path):
    if state == goal_state:
        return path
    if depth == limit:
        return None

    visited.add(state)
    for move in moves:
        new_state = move_blank(state, move)
        if new_state and new_state not in visited:
            result = dfs(new_state, depth + 1, limit, visited, path + [move])
            if result is not None:
                return result
    visited.remove(state)
    return None

def ids(start_state):
    depth = 0
    while True:
        visited = set()
        path = dfs(start_state, 0, depth, visited, [])
        if path is not None:
            return path
        depth += 1

# Example usage:
if __name__ == "__main__":
    # Starting configuration: 0 is the blank tile
    start = (1, 2, 3,
             4, 0, 6,
             7, 5, 8)

    solution = ids(start)
    if solution:
        print(f"Solution found in {len(solution)} moves:")
        print(solution)
    else:
        print("No solution found.")
