"""
ML-KEM - NTT Domain Linear Algebra

Operations:
1. NTT Vector Addition
2. NTT Matrix-Vector Multiplication
"""

from backend.core.ntt import N, Q
from backend.core.ntt_multiplication import multiply_ntts


def validate_polynomial(poly):

    if not isinstance(poly, list):
        raise TypeError("Polynomial must be a list")

    if len(poly) != N:
        raise ValueError("Polynomial must contain 256 coefficients")

    for value in poly:

        if not isinstance(value, int):
            raise TypeError("Coefficients must be integers")

        if not 0 <= value < Q:
            raise ValueError("Invalid coefficient")


def validate_vector(vector):

    if not isinstance(vector, list):
        raise TypeError("Vector must be a list")

    if len(vector) not in (2, 3, 4):
        raise ValueError("Vector dimension must be 2, 3, or 4")

    for polynomial in vector:
        validate_polynomial(polynomial)


def vector_add(vector_a, vector_b):

    validate_vector(vector_a)
    validate_vector(vector_b)

    if len(vector_a) != len(vector_b):
        raise ValueError("Vector dimensions must match")

    result = []

    for i in range(len(vector_a)):

        polynomial = [
            (vector_a[i][j] + vector_b[i][j]) % Q
            for j in range(N)
        ]

        result.append(polynomial)

    return result


def matrix_vector_multiply_ntt(matrix, vector):

    validate_vector(vector)

    k = len(vector)

    if not isinstance(matrix, list):
        raise TypeError("Matrix must be a list")

    if len(matrix) != k:
        raise ValueError("Matrix row count must match vector dimension")

    for row in matrix:

        if not isinstance(row, list) or len(row) != k:
            raise ValueError("Matrix must be a square k x k matrix")

        for polynomial in row:
            validate_polynomial(polynomial)

    result = []

    for i in range(k):

        accumulator = [0] * N

        for j in range(k):

            product = multiply_ntts(
                matrix[i][j],
                vector[j]
            )

            accumulator = [
                (accumulator[t] + product[t]) % Q
                for t in range(N)
            ]

        result.append(accumulator)

    return result