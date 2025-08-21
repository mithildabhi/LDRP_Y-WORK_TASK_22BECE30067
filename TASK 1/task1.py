# task 1 Sudoku puzzle

import random
board = [
["5","3",".",".",".",".",".","1","."],
["6",".",".","1","9","5",".",".","."],
[".","9","8",".",".",".",".","6","."],
["8",".",".",".","6",".",".",".","3"],
["4",".",".","8",".","3",".",".","1"],
["7",".",".",".","2",".",".",".","6"],
[".",".","1",".",".",".","2","8","."],
[".","8",".",".","1","9",".",".","5"],
[".",".",".",".",".","6","1","7","."]
]

# the . represent the empty space 
def print_board(b):
    for i in range(len(b)):
        if i % 3 == 0 and i != 0:
            print("- - - - - - - - - - -")
        for j in range(len(b[0])):
            if j % 3 == 0 and j != 0:
                print(" | ", end="")
            print(b[i][j], end=" ")
        print()

def is_valid_move(board, row, col, num):
    # Check if num is already in the row
    for j in range(9):
        if board[row][j] == num:
            return False

    # Check if num is already in the column
    for i in range(9):
        if board[i][col] == num:
            return False

    # Check 3x3 grid
    grid_x = (row // 3) * 3
    grid_y = (col // 3) * 3
    for i in range(grid_x, grid_x + 3):
        for j in range(grid_y, grid_y + 3):
            if board[i][j] == num:
                return False

    return True

def find_empty(board):
    for i in range(9):
        for j in range(9):
            if board[i][j] == '.':
                return (i, j)  # row, col
    return None

def solve(board): # Main Calling function
    find = find_empty(board)
    if not find:
        return True  # Solved
    else:
        row, col = find

    for num in map(str, range(1,10)):
        if is_valid_move(board, row, col, num):
            board[row][col] = num
            if solve(board):
                return True
            board[row][col] = '.'  # backtrack

    return False

# Example usage:
print("Initial Sudoku Board:")
print_board(board)

if solve(board):
    print("\nSudoku Solved:")
    print_board(board)
else:
    print("No solution exists for the given board.")