import pytest

from backend.core.matrix import (
    expand_a,
    transpose_matrix
)


# Test 1: ML-KEM-512 matrix size

def test_expand_a_mlkem512():

    rho = bytes(32)

    matrix = expand_a(rho, 2)

    assert len(matrix) == 2

    assert all(len(row) == 2 for row in matrix)


# Test 2: ML-KEM-768 matrix size

def test_expand_a_mlkem768():

    rho = bytes(32)

    matrix = expand_a(rho, 3)

    assert len(matrix) == 3

    assert all(len(row) == 3 for row in matrix)


# Test 3: ML-KEM-1024 matrix size

def test_expand_a_mlkem1024():

    rho = bytes(32)

    matrix = expand_a(rho, 4)

    assert len(matrix) == 4

    assert all(len(row) == 4 for row in matrix)


# Test 4: Every polynomial has 256 coefficients

def test_matrix_polynomial_length():

    rho = bytes([1] * 32)

    matrix = expand_a(rho, 3)

    for row in matrix:

        for polynomial in row:

            assert len(polynomial) == 256


# Test 5: Coefficient range

def test_matrix_coefficient_range():

    rho = bytes([2] * 32)

    matrix = expand_a(rho, 2)

    for row in matrix:

        for polynomial in row:

            assert all(
                0 <= coefficient < 3329
                for coefficient in polynomial
            )


# Test 6: Deterministic matrix generation

def test_matrix_deterministic():

    rho = bytes([5] * 32)

    matrix1 = expand_a(rho, 2)

    matrix2 = expand_a(rho, 2)

    assert matrix1 == matrix2


# Test 7: Different seeds produce different matrices

def test_matrix_different_seeds():

    rho1 = bytes([1] * 32)

    rho2 = bytes([2] * 32)

    matrix1 = expand_a(rho1, 2)

    matrix2 = expand_a(rho2, 2)

    assert matrix1 != matrix2


# Test 8: Invalid seed length

def test_matrix_invalid_seed():

    with pytest.raises(ValueError):

        expand_a(bytes(16), 2)


# Test 9: Invalid k

def test_matrix_invalid_k():

    with pytest.raises(ValueError):

        expand_a(bytes(32), 5)


# Test 10: Matrix transpose

def test_transpose_matrix():

    matrix = [
        [1, 2],
        [3, 4]
    ]

    result = transpose_matrix(matrix)

    expected = [
        [1, 3],
        [2, 4]
    ]

    assert result == expected


# Test 11: Transpose rectangular matrix

def test_transpose_rectangular_matrix():

    matrix = [
        [1, 2, 3],
        [4, 5, 6]
    ]

    result = transpose_matrix(matrix)

    expected = [
        [1, 4],
        [2, 5],
        [3, 6]
    ]

    assert result == expected


# Test 12: Invalid matrix

def test_transpose_invalid_matrix():

    matrix = [
        [1, 2],
        [3]
    ]

    with pytest.raises(ValueError):

        transpose_matrix(matrix)