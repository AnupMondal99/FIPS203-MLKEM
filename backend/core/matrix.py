"""
ML-KEM Matrix Generation

Uses FIPS 203 Algorithm 7: SampleNTT

Generates the matrix A_hat used in K-PKE.
"""

from backend.core.sampling import sample_ntt


def expand_a(rho, k):

    # Validate seed

    if not isinstance(rho, bytes):
        raise TypeError("Seed must be bytes")

    if len(rho) != 32:
        raise ValueError("Seed must contain exactly 32 bytes")

    # Validate parameter k

    if not isinstance(k, int):
        raise TypeError("k must be an integer")

    if k not in (2, 3, 4):
        raise ValueError("k must be 2, 3, or 4")

    # Generate k x k matrix

    matrix = []

    for i in range(k):

        row = []

        for j in range(k):

            polynomial = sample_ntt(rho, j, i)

            row.append(polynomial)

        matrix.append(row)

    return matrix


def transpose_matrix(matrix):

    if not isinstance(matrix, list):
        raise TypeError("Matrix must be a list")

    if not matrix:
        raise ValueError("Matrix cannot be empty")

    rows = len(matrix)

    if not all(isinstance(row, list) for row in matrix):
        raise TypeError("Each matrix row must be a list")

    columns = len(matrix[0])

    if columns == 0:
        raise ValueError("Matrix rows cannot be empty")

    if any(len(row) != columns for row in matrix):
        raise ValueError("Matrix must be rectangular")

    return [
        [matrix[i][j] for i in range(rows)]
        for j in range(columns)
    ]