import heapq

start = ((1,2,3),(4,5,6),(7,0,8))
goal = ((1,2,3),(4,5,6),(7,8,0))

def heuristic(state):
    dist = 0
    for i in range(3):
        for j in range(3):
            val = state[i][j]
            if val != 0:
                for x in range(3):
                    for y in range(3):
                        if goal[x][y] == val:
                            dist += abs(i - x) + abs(j - y)
                            break
    return dist

def neighbors(state):
    board = [list(row) for row in state]
    x = y = -1
    for i in range(3):
        for j in range(3):
            if board[i][j] == 0:
                x, y = i, j
                break
        if x != -1:
            break
    moves = []
    for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < 3 and 0 <= ny < 3:
            new_board = [row[:] for row in board]
            new_board[x][y], new_board[nx][ny] = new_board[nx][ny], new_board[x][y]
            moves.append(tuple(tuple(row) for row in new_board))
    return moves

def a_star(start):
    open_set = []
    heapq.heappush(open_set, (heuristic(start), 0, start, []))
    visited = set()
    while open_set:
        f, g, state, path = heapq.heappop(open_set)
        if state == goal:
            return path + [state]
        if state in visited:
            continue
        visited.add(state)
        for n in neighbors(state):
            if n not in visited:
                heapq.heappush(open_set, (g+1+heuristic(n), g+1, n, path+[state]))
    return None

result = a_star(start)
if result is None:
    print("No solution found")
else:
    for step in result:
        for row in step:
            print(row)
        print()
