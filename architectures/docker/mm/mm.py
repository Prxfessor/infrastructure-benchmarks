import sys
import os

# set the environment variables
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'

# import numpy after setting variables
import numpy as np

# declare the size of the matrix
n = int(sys.argv[1])

# declare matrix A of integers up to 10 of size n x n
A = np.random.randint(10,size=(n, n))

# declare matrix B of integers up to 10 of size n x n
B = np.random.randint(10,size=(n, n))

# get the dot product of the two the matrix
C = np.dot(A, B)
print("COMPLETED DOCKER MM with N: " + str(n))

