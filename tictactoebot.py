def print_board(board):
    for row in board:
        print(' | '.join(row))
    print()

def is_winner(board, player):
    wins = [
        [board[0][0], board[0][1], board[0][2]],
        [board[1][0], board[1][1], board[1][2]],
        [board[2][0], board[2][1], board[2][2]],
        [board[0][0], board[1][0], board[2][0]],
        [board[0][1], board[1][1], board[2][1]],
        [board[0][2], board[1][2], board[2][2]],
        [board[0][0], board[1][1], board[2][2]],
        [board[0][2], board[1][1], board[2][0]],
    ]
    return [player, player, player] in wins

def is_board_full(board):
    return all(cell != ' ' for row in board for cell in row)

def minimax(board, is_max):
    if is_winner(board, 'O'):
        return 1
    if is_winner(board, 'X'):
        return -1
    if is_board_full(board):
        return 0
    if is_max:
        best = -float('inf')
        for i in range(3):
            for j in range(3):
                if board[i][j] == ' ':
                    board[i][j] = 'O'
                    val = minimax(board, False)
                    board[i][j] = ' '
                    best = max(best, val)
        return best
    else:
        best = float('inf')
        for i in range(3):
            for j in range(3):
                if board[i][j] == ' ':
                    board[i][j] = 'X'
                    val = minimax(board, True)
                    board[i][j] = ' '
                    best = min(best, val)
        return best

def bot_move(board):
    best_score = -float('inf')
    move = None
    for i in range(3):
        for j in range(3):
            if board[i][j] == ' ':
                board[i][j] = 'O'
                score = minimax(board, False)
                board[i][j] = ' '
                if score > best_score:
                    best_score = score
                    move = (i,j)
    if move:
        board[move[0]][move[1]] = 'O'

board = [[' ']*3 for _ in range(3)]

while True:
    print_board(board)
    if is_winner(board, 'O'):
        print("Bot wins!")
        break
    if is_winner(board, 'X'):
        print("You win!")
        break
    if is_board_full(board):
        print("Tie!")
        break

    try:
        row = int(input("Your move row (0-2): "))
        col = int(input("Your move col (0-2): "))
        if 0 <= row <= 2 and 0 <= col <= 2 and board[row][col] == ' ':
            board[row][col] = 'X'
        else:
            print("Invalid move. Try again.")
            continue
    except:
        print("Invalid input. Try again.")
        continue

    if is_winner(board, 'X') or is_board_full(board):
        continue

    bot_move(board)
