import pytest

from backend.core.polynomial import (
    N,
    Q,
    polynomial_add,
    polynomial_subtract,
    polynomial_multiply,
    polynomial_equal
)


def test_polynomial_addition():

    a = [0] * N
    b = [0] * N

    a[0] = 10
    b[0] = 20

    result = polynomial_add(a, b)

    assert result[0] == 30


def test_polynomial_subtraction():

    a = [0] * N
    b = [0] * N

    a[0] = 10
    b[0] = 20

    result = polynomial_subtract(a, b)

    assert result[0] == Q - 10


def test_polynomial_multiplication():

    a = [0] * N
    b = [0] * N

    a[0] = 2
    b[0] = 3

    result = polynomial_multiply(a, b)

    assert result[0] == 6


def test_negacyclic_multiplication():

    a = [0] * N
    b = [0] * N

    a[255] = 2
    b[1] = 3

    result = polynomial_multiply(a, b)

    assert result[0] == Q - 6


def test_polynomial_equality():

    a = [0] * N
    b = [0] * N

    assert polynomial_equal(a, b)


def test_invalid_polynomial():

    with pytest.raises(ValueError):

        polynomial_add([1, 2], [3, 4])