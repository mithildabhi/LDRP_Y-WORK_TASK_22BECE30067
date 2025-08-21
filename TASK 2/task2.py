ratings = [1,2,2]
n = len(ratings)

candies = [1]

for i in range(1, len(ratings)):
    if ratings[i] > ratings[i-1]:
        candies.append(2)
    else:
        candies.append(1)
print("Ratings= ",ratings)
print("Candies distribution:", candies)
print("Total candies:", sum(candies))

