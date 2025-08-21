matrix = [
    ["1","0","1","0","0"],
    ["1","0","1","1","1"],
    ["1","1","1","1","1"],
    ["1","0","0","1","0"]
]

def compare(matrix):
    for i in range(9):
        for j in range(9):
            if matrix[i][j] == '1':
                
            else:    
                return True  # row, col
            if matrix[i][j] == matrix[i][j+1]:
    return None

compare(matrix)

