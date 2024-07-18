def edit_distance(str1, str2):
 len_str1 = len(str1) + 1
 len_str2 = len(str2) + 1
  
 # Initialize a matrix to store the edit distances
 matrix = [[0 for _ in range(len_str2)] for _ in range(len_str1)]
 # Initialize the first row and column of the matrix
 for i in range(len_str1):
 matrix[i][0] = i
 for j in range(len_str2):
 matrix[0][j] = j
  
 # Calculate the edit distances using dynamic programming
 for i in range(1, len_str1):
 for j in range(1, len_str2):
 cost = 0 if str1[i - 1] == str2[j - 1] else 1
 matrix[i][j] = min(
 matrix[i - 1][j] + 1, # Deletion
 matrix[i][j - 1] + 1, # Insertion
 matrix[i - 1][j - 1] + cost # Substitution
 )
  
 # The bottom-right cell of the matrix contains the edit distance
 return matrix[-1][-1]

str1 = "kitten"
str2 = "sitting"
distance = edit_distance(str1, str2)
print(f"The edit distance between '{str1}' and '{str2}' is: {distance}")
