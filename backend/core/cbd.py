"""
FIPS 203 - ML-KEM

Algorithm 4: BytesToBits
Algorithm 8: SamplePolyCBD

Parameters:
N = 256
Q = 3329
"""

N = 256
Q = 3329


def validate_eta(eta):

    if eta not in (2, 3):
        raise ValueError("Eta must be either 2 or 3")


def bytes_to_bits(byte_array):

    bits = []

    for byte in byte_array:

        if not isinstance(byte, int):
            raise TypeError("Each byte must be an integer")

        if byte < 0 or byte > 255:
            raise ValueError("Each byte must be between 0 and 255")

        for j in range(8):

            bit = (byte >> j) & 1

            bits.append(bit)

    return bits


def sample_poly_cbd(byte_array, eta):

    validate_eta(eta)

    expected_length = 64 * eta

    if len(byte_array) != expected_length:

        raise ValueError(
            f"Input must contain exactly {expected_length} bytes "
            f"for eta={eta}"
        )

    bits = bytes_to_bits(byte_array)

    polynomial = [0] * N

    for i in range(N):

        x = sum(
            bits[2 * i * eta + j]
            for j in range(eta)
        )

        y = sum(
            bits[2 * i * eta + eta + j]
            for j in range(eta)
        )

        polynomial[i] = (x - y) % Q

    return polynomial