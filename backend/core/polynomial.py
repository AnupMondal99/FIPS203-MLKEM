"""
FIPS 203 - Polynomial Arithmetic
"""

N = 256
Q = 3329


def validate_polynomial(poly):
    if len(poly) != N:
        raise ValueError("Polynomial must contain 256 coefficients")

    if any(not isinstance(c, int) for c in poly):
        raise TypeError("Coefficients must be integers")


def polynomial_add(a, b):
    validate_polynomial(a)
    validate_polynomial(b)

    return [(a[i] + b[i]) % Q for i in range(N)]


def polynomial_subtract(a, b):
    validate_polynomial(a)
    validate_polynomial(b)

    return [(a[i] - b[i]) % Q for i in range(N)]


def polynomial_multiply(a, b):
    validate_polynomial(a)
    validate_polynomial(b)

    result = [0] * N

    for i in range(N):
        for j in range(N):

            product = a[i] * b[j]
            position = i + j

            if position < N:
                result[position] += product
            else:
                result[position - N] -= product

    return [x % Q for x in result]


def polynomial_equal(a, b):
    validate_polynomial(a)
    validate_polynomial(b)

    return a == b