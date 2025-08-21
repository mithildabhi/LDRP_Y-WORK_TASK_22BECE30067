matrix = [
    ["1","0","1","0","0"],
    ["1","0","1","1","1"],
    ["1","1","1","1","1"],
    ["1","0","0","1","0"]
]

def maximalRectangle(matrix):
    if not matrix:
        return 0

    n = len(matrix[0])
    heights = [0] * (n + 1)  # +1 for easier stack handling
    max_area = 0

    for row in matrix:
        # update histogram heights
        for i in range(n):
            heights[i] = heights[i] + 1 if row[i] == "1" else 0
        # calculate largest rectangle in histogram
        stack = [-1]
        for i in range(n + 1):
            while heights[i] < heights[stack[-1]]:
                h = heights[stack.pop()]
                w = i - stack[-1] - 1
                max_area = max(max_area, h * w)
            stack.append(i)
    return max_area

print(maximalRectangle(matrix))
