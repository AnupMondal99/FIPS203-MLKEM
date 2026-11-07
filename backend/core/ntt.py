"""
FIPS 203 - Number Theoretic Transform

Algorithm 9: NTT
Algorithm 10: Inverse NTT

Parameters:
n = 256
q = 3329
zeta = 17
"""

N = 256
Q = 3329
ZETA = 17

INVERSE_128 = 3303


def validate_input(poly):
    """
    Validate the input polynomial.

    Input must contain exactly 256
    coefficients in Z_q.
    """

    if len(poly) != N:
        raise ValueError(
            "Input must contain exactly 256 coefficients"
        )

    if any(not isinstance(c, int) for c in poly):
        raise TypeError(
            "All coefficients must be integers"
        )

    if any(c < 0 or c >= Q for c in poly):
        raise ValueError(
            "Coefficients must be between 0 and 3328"
        )


def bit_reverse_7(value):
    """
    Reverse the 7-bit binary representation.

    Used to calculate zeta powers
    according to FIPS 203.
    """

    result = 0

    for _ in range(7):

        result = (result << 1) | (value & 1)

        value >>= 1

    return result


def get_zeta(index):
    """
    Calculate zeta^BitRev7(index) mod q.
    """

    exponent = bit_reverse_7(index)

    return pow(ZETA, exponent, Q)


def ntt(poly):
    """
    FIPS 203 Algorithm 9.

    Forward Number Theoretic Transform.
    """

    validate_input(poly)

    f = poly.copy()

    i = 1

    length = 128

    while length >= 2:

        for start in range(0, N, 2 * length):

            zeta = get_zeta(i)

            i += 1

            for j in range(start, start + length):

                t = (zeta * f[j + length]) % Q

                f[j + length] = (
                    f[j] - t
                ) % Q

                f[j] = (
                    f[j] + t
                ) % Q

        length //= 2

    return f


def inverse_ntt(poly_hat):
    """
    FIPS 203 Algorithm 10.

    Inverse Number Theoretic Transform.
    """

    validate_input(poly_hat)

    f = poly_hat.copy()

    i = 127

    length = 2

    while length <= 128:

        for start in range(0, N, 2 * length):

            zeta = get_zeta(i)

            i -= 1

            for j in range(start, start + length):

                t = f[j]

                f[j] = (
                    t + f[j + length]
                ) % Q

                f[j + length] = (
                    zeta * (f[j + length] - t)
                ) % Q

        length *= 2

    # Multiply every coefficient by 3303.
    # 3303 = 128^(-1) mod 3329.

    f = [
        (coefficient * INVERSE_128) % Q
        for coefficient in f
    ]

    return f