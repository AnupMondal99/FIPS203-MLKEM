"""
FIPS 203 - ML-KEM

Algorithm 5: ByteEncode
Algorithm 6: ByteDecode

Section 4.2.1:
Compress and Decompress
"""

N = 256
Q = 3329


def validate_d(d):

    if not isinstance(d, int):
        raise TypeError("d must be an integer")

    if not 1 <= d <= 12:
        raise ValueError("d must be between 1 and 12")


def validate_polynomial(poly):

    if len(poly) != N:
        raise ValueError("Polynomial must contain 256 coefficients")

    for value in poly:

        if not isinstance(value, int):
            raise TypeError("Coefficients must be integers")


# Algorithm 5: ByteEncode

def byte_encode(poly, d):

    validate_d(d)
    validate_polynomial(poly)

    modulus = Q if d == 12 else (1 << d)

    bits = []

    for value in poly:

        if not 0 <= value < modulus:
            raise ValueError("Coefficient outside valid range")

        for j in range(d):

            bits.append((value >> j) & 1)

    result = bytearray()

    for i in range(0, len(bits), 8):

        byte = 0

        for j in range(8):

            byte |= bits[i + j] << j

        result.append(byte)

    return bytes(result)


# Algorithm 6: ByteDecode

def byte_decode(data, d):

    validate_d(d)

    if not isinstance(data, bytes):
        raise TypeError("Input must be bytes")

    expected_length = 32 * d

    if len(data) != expected_length:
        raise ValueError(
            f"Expected {expected_length} bytes"
        )

    bits = []

    for byte in data:

        for j in range(8):

            bits.append((byte >> j) & 1)

    polynomial = []

    for i in range(N):

        value = 0

        for j in range(d):

            value += bits[i * d + j] << j

        if d == 12 and value >= Q:

            raise ValueError(
                "Invalid 12-bit coefficient: value must be less than 3329"
            )

        polynomial.append(value)

    return polynomial

# Section 4.2.1: Compress

def compress(value, d):

    validate_d(d)

    if not isinstance(value, int):
        raise TypeError("Value must be an integer")

    if not 0 <= value < Q:
        raise ValueError("Value must be between 0 and 3328")

    numerator = (1 << d) * value

    return ((2 * numerator + Q) // (2 * Q)) % (1 << d)


# Section 4.2.1: Decompress

def decompress(value, d):

    validate_d(d)

    if not isinstance(value, int):
        raise TypeError("Value must be an integer")

    if not 0 <= value < (1 << d):
        raise ValueError("Compressed value outside valid range")

    numerator = Q * value

    return (2 * numerator + (1 << d)) // (2 * (1 << d))