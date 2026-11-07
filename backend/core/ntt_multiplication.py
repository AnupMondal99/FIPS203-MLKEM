"""
FIPS 203 - ML-KEM

Algorithm 11: MultiplyNTTs
Algorithm 12: BaseCaseMultiply

Parameters:
N = 256
Q = 3329
ZETA = 17
"""

from backend.core.ntt import N, Q, bit_reverse_7

ZETA = 17


def validate_coefficient(value):
    if not isinstance(value, int):
        raise TypeError("Coefficient must be an integer")

    if value < 0 or value >= Q:
        raise ValueError(
            "Coefficient must be between 0 and 3328"
        )


def validate_ntt_array(poly):
    if len(poly) != N:
        raise ValueError(
            "NTT representation must contain 256 coefficients"
        )

    for coefficient in poly:
        validate_coefficient(coefficient)


# Algorithm 12: BaseCaseMultiply

def base_case_multiply(a0, a1, b0, b1, gamma):

    validate_coefficient(a0)
    validate_coefficient(a1)
    validate_coefficient(b0)
    validate_coefficient(b1)
    validate_coefficient(gamma)

    c0 = (a0 * b0 + a1 * b1 * gamma) % Q

    c1 = (a0 * b1 + a1 * b0) % Q

    return c0, c1


# Calculate gamma for Algorithm 11

def get_gamma(index):

    exponent = 2 * bit_reverse_7(index) + 1

    return pow(ZETA, exponent, Q)


# Algorithm 11: MultiplyNTTs

def multiply_ntts(f_hat, g_hat):

    validate_ntt_array(f_hat)
    validate_ntt_array(g_hat)

    h_hat = [0] * N

    for i in range(128):

        gamma = get_gamma(i)

        c0, c1 = base_case_multiply(
            f_hat[2 * i],
            f_hat[2 * i + 1],
            g_hat[2 * i],
            g_hat[2 * i + 1],
            gamma
        )

        h_hat[2 * i] = c0
        h_hat[2 * i + 1] = c1

    return h_hat