"""
FIPS 203 - ML-KEM

Algorithm 7: SampleNTT

Uses SHAKE128 and rejection sampling.

Parameters:
N = 256
Q = 3329
"""

from backend.core.hashing import XOF

N = 256
Q = 3329


def sample_ntt(seed, j, i):

    # Validate seed

    if not isinstance(seed, bytes):
        raise TypeError("Seed must be bytes")

    if len(seed) != 32:
        raise ValueError("Seed must contain exactly 32 bytes")

    # Validate indices

    if not isinstance(j, int) or not isinstance(i, int):
        raise TypeError("Indices must be integers")

    if not (0 <= i <= 255 and 0 <= j <= 255):
        raise ValueError("Indices must be between 0 and 255")

    # Rejection sampling

    output = []

    output_length = 768

    while len(output) < N:

        random_bytes = XOF(
            seed,
            j,
            i,
            output_length
        )

        output = []

        for position in range(0, len(random_bytes) - 2, 3):

            c0 = random_bytes[position]
            c1 = random_bytes[position + 1]
            c2 = random_bytes[position + 2]

            d1 = c0 + 256 * (c1 % 16)

            d2 = (c1 // 16) + 16 * c2

            if d1 < Q:
                output.append(d1)

            if d2 < Q and len(output) < N:
                output.append(d2)

            if len(output) == N:
                break

        # Increase SHAKE output if fewer than 256
        # valid coefficients were generated.

        if len(output) < N:
            output_length *= 2

    return output