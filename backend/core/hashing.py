"""
FIPS 203 - ML-KEM

Cryptographic Hashing Functions:

H     : SHA3-256
G     : SHA3-512
PRF   : SHAKE256
XOF   : SHAKE128
J     : SHAKE256
"""

import hashlib


# Common validation

def validate_bytes(data, name="Input"):

    if not isinstance(data, bytes):
        raise TypeError(f"{name} must be bytes")


# H Function: SHA3-256

def H(data):

    validate_bytes(data)

    return hashlib.sha3_256(data).digest()


# G Function: SHA3-512

def G(data):

    validate_bytes(data)

    return hashlib.sha3_512(data).digest()


# PRF Function: SHAKE256

def PRF(seed, nonce, eta):

    validate_bytes(seed, "Seed")

    if len(seed) != 32:
        raise ValueError("Seed must contain exactly 32 bytes")

    if not isinstance(nonce, int):
        raise TypeError("Nonce must be an integer")

    if nonce < 0 or nonce > 255:
        raise ValueError("Nonce must be between 0 and 255")

    if eta not in (2, 3):
        raise ValueError("Eta must be either 2 or 3")

    input_data = seed + bytes([nonce])

    output_length = 64 * eta

    return hashlib.shake_256(input_data).digest(output_length)


# XOF Function: SHAKE128

def XOF(seed, x, y, output_length):

    validate_bytes(seed, "Seed")

    if len(seed) != 32:
        raise ValueError("Seed must contain exactly 32 bytes")

    if not isinstance(x, int) or not isinstance(y, int):
        raise TypeError("x and y must be integers")

    if not (0 <= x <= 255 and 0 <= y <= 255):
        raise ValueError("x and y must be between 0 and 255")

    if not isinstance(output_length, int):
        raise TypeError("Output length must be an integer")

    if output_length < 0:
        raise ValueError("Output length cannot be negative")

    input_data = seed + bytes([x, y])

    return hashlib.shake_128(input_data).digest(output_length)


# J Function: SHAKE256

def J(data):

    validate_bytes(data)

    return hashlib.shake_256(data).digest(32)