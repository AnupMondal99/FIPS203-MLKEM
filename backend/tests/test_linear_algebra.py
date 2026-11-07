import pytest

from backend.core.ntt import N, Q, ntt
from backend.core.polynomial import polynomial_multiply

from backend.core.linear_algebra import (
    vector_add,
    matrix_vector_multiply_ntt
)


# Test 1: Vector addition

def test_vector_add():

    a = [[1] * N, [2] * N]
    b = [[3] * N, [4] * N]

    result = vector_add(a, b)

    assert result[0] == [4] * N
    assert result[1] == [6] * N


# Test 2: Modular vector addition

def test_vector_add_modulo():

    a = [[Q - 1] * N, [Q - 2] * N]
    b = [[2] * N, [3] * N]

    result = vector_add(a, b)

    assert result[0] == [1] * N
    assert result[1] == [1] * N


# Test 3: Vector addition dimension mismatch

def test_vector_add_invalid_dimension():

    a = [[0] * N, [0] * N]
    b = [[0] * N]

    with pytest.raises(ValueError):
        vector_add(a, b)


# Test 4: Matrix-vector multiplication output size

def test_matrix_vector_output_size():

    matrix = [
        [[0] * N, [0] * N],
        [[0] * N, [0] * N]
    ]

    vector = [
        [0] * N,
        [0] * N
    ]

    result = matrix_vector_multiply_ntt(matrix, vector)

    assert len(result) == 2
    assert all(len(poly) == N for poly in result)


# Test 5: Zero matrix multiplication

def test_zero_matrix_multiplication():

    matrix = [
        [[0] * N, [0] * N],
        [[0] * N, [0] * N]
    ]

    vector = [
        [1] * N,
        [2] * N
    ]

    result = matrix_vector_multiply_ntt(matrix, vector)

    assert result == [[0] * N, [0] * N]


# Test 6: Matrix-vector multiplication consistency

def test_matrix_vector_consistency():

    f = [(i + 1) % Q for i in range(N)]
    g = [(2 * i + 3) % Q for i in range(N)]

    h = [(3 * i + 5) % Q for i in range(N)]
    p = [(4 * i + 7) % Q for i in range(N)]

    matrix = [
        [ntt(f), ntt(g)],
        [ntt(h), ntt(p)]
    ]

    vector = [
        ntt(g),
        ntt(f)
    ]

    result = matrix_vector_multiply_ntt(matrix, vector)

    expected_first = [
        (x + y) % Q
        for x, y in zip(
            polynomial_multiply(f, g),
            polynomial_multiply(g, f)
        )
    ]

    expected_second = [
        (x + y) % Q
        for x, y in zip(
            polynomial_multiply(h, g),
            polynomial_multiply(p, f)
        )
    ]

    assert result[0] == ntt(expected_first)
    assert result[1] == ntt(expected_second)


# Test 7: Invalid matrix dimensions

def test_invalid_matrix_dimensions():

    matrix = [
        [[0] * N]
    ]

    vector = [
        [0] * N,
        [0] * N
    ]

    with pytest.raises(ValueError):
        matrix_vector_multiply_ntt(matrix, vector)


# Test 8: Invalid vector coefficient

def test_invalid_vector_coefficient():

    vector = [[0] * N, [0] * N]
    vector[0][0] = Q

    matrix = [
        [[0] * N, [0] * N],
        [[0] * N, [0] * N]
    ]

    with pytest.raises(ValueError):
        matrix_vector_multiply_ntt(matrix, vector)