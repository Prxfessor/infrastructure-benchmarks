import json
import numpy as np

def lambda_handler(event, context):
    # get the size of the matricies
    n = event["size"]
    
    # declare matrix A of integers up to 10 of size n x n
    A = np.random.randint(10,size=(n, n))


    # declare matrix B of integers up to 10 of size n x n
    B = np.random.randint(10,size=(n, n))

    
    # get the dot product of the two the matrix
    C = np.dot(A, B)

    
    return {
        'statusCode': 200,
        "sizeOfMatrix" : n,
        "message": "COMPLETED"
    }

