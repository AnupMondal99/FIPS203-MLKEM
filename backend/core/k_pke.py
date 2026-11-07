"""
FIPS 203 - ML-KEM

K-PKE.KeyGen
K-PKE.Encrypt
K-PKE.Decrypt
"""

from backend.core.hashing import G, PRF
from backend.core.cbd import sample_poly_cbd
from backend.core.ntt import ntt, inverse_ntt
from backend.core.matrix import expand_a, transpose_matrix
from backend.core.linear_algebra import (
    vector_add,
    matrix_vector_multiply_ntt
)
from backend.core.encoding import (
    byte_encode,
    byte_decode,
    compress,
    decompress
)
from backend.core.ntt_multiplication import multiply_ntts


N = 256
Q = 3329


# ============================================================
# Common Validation
# ============================================================

def validate_k(k):
    if not isinstance(k, int) or isinstance(k, bool):
        raise TypeError("k must be an integer")

    if k not in (2, 3, 4):
        raise ValueError("k must be 2, 3, or 4")


def validate_compression_parameters(du, dv):

    if not isinstance(du, int) or isinstance(du, bool):
        raise TypeError("du must be an integer")

    if not isinstance(dv, int) or isinstance(dv, bool):
        raise TypeError("dv must be an integer")

    if du not in (10, 11):
        raise ValueError("du must be 10 or 11")

    if dv not in (4, 5):
        raise ValueError("dv must be 4 or 5")


# ============================================================
# Vector Encoding
# ============================================================

def encode_vector(vector, d=12):

    encoded = bytearray()

    for polynomial in vector:
        encoded.extend(
            byte_encode(polynomial, d)
        )

    return bytes(encoded)


def decode_vector(data, k, d=12):

    validate_k(k)

    if not isinstance(data, bytes):
        raise TypeError("Encoded vector must be bytes")

    expected_length = 32 * d * k

    if len(data) != expected_length:
        raise ValueError("Invalid encoded vector length")

    vector = []

    polynomial_length = 32 * d

    for i in range(k):

        start = i * polynomial_length
        end = start + polynomial_length

        polynomial = byte_decode(
            data[start:end],
            d
        )

        vector.append(polynomial)

    return vector


# ============================================================
# Compression and Decompression
# ============================================================

def encode_compressed_vector(vector, d):

    encoded = bytearray()

    for polynomial in vector:

        compressed = [
            compress(value, d)
            for value in polynomial
        ]

        encoded.extend(
            byte_encode(compressed, d)
        )

    return bytes(encoded)


def decompress_vector(vector, d):

    return [
        [
            decompress(value, d)
            for value in polynomial
        ]
        for polynomial in vector
    ]


# ============================================================
# Polynomial Operations
# ============================================================

def add_polynomials(a, b):

    if len(a) != N or len(b) != N:
        raise ValueError(
            "Both polynomials must contain 256 coefficients"
        )

    return [
        (a[i] + b[i]) % Q
        for i in range(N)
    ]


def subtract_polynomials(a, b):

    if len(a) != N or len(b) != N:
        raise ValueError(
            "Both polynomials must contain 256 coefficients"
        )

    return [
        (a[i] - b[i]) % Q
        for i in range(N)
    ]


def polynomial_vector_dot_ntt(vector_a, vector_b):

    if len(vector_a) != len(vector_b):
        raise ValueError(
            "Vector dimensions must match"
        )

    result = [0] * N

    for i in range(len(vector_a)):

        product = multiply_ntts(
            vector_a[i],
            vector_b[i]
        )

        result = [
            (result[j] + product[j]) % Q
            for j in range(N)
        ]

    return result


# ============================================================
# K-PKE.KeyGen
# FIPS 203 - Algorithm 13
# ============================================================

def k_pke_keygen(d, k, eta1):

    # Validate seed

    if not isinstance(d, bytes):
        raise TypeError("Seed d must be bytes")

    if len(d) != 32:
        raise ValueError(
            "Seed d must contain exactly 32 bytes"
        )

    validate_k(k)

    if eta1 not in (2, 3):
        raise ValueError("eta1 must be 2 or 3")

    # Step 1: Generate rho and sigma

    expanded_seed = G(
        d + bytes([k])
    )

    rho = expanded_seed[:32]
    sigma = expanded_seed[32:]

    # Step 2: Generate matrix A_hat

    a_hat = expand_a(
        rho,
        k
    )

    # Step 3: Generate secret vector s

    s = []

    nonce = 0

    for _ in range(k):

        random_bytes = PRF(
            sigma,
            nonce,
            eta1
        )

        polynomial = sample_poly_cbd(
            random_bytes,
            eta1
        )

        s.append(polynomial)

        nonce += 1

    # Step 4: Generate error vector e

    e = []

    for _ in range(k):

        random_bytes = PRF(
            sigma,
            nonce,
            eta1
        )

        polynomial = sample_poly_cbd(
            random_bytes,
            eta1
        )

        e.append(polynomial)

        nonce += 1

    # Step 5: Apply NTT

    s_hat = [
        ntt(polynomial)
        for polynomial in s
    ]

    e_hat = [
        ntt(polynomial)
        for polynomial in e
    ]

    # Step 6: Calculate t_hat = A_hat * s_hat + e_hat

    t_hat = matrix_vector_multiply_ntt(
        a_hat,
        s_hat
    )

    t_hat = vector_add(
        t_hat,
        e_hat
    )

    # Step 7: Encode public and private keys

    ek_pke = (
        encode_vector(t_hat, 12) + rho
    )

    dk_pke = encode_vector(
        s_hat,
        12
    )

    return ek_pke, dk_pke


# ============================================================
# K-PKE.Encrypt
# FIPS 203 - Algorithm 14
# ============================================================

def k_pke_encrypt(
    ek_pke,
    message,
    randomness,
    k,
    eta1,
    eta2,
    du,
    dv
):

    # Validate inputs

    if not isinstance(ek_pke, bytes):
        raise TypeError(
            "Encryption key must be bytes"
        )

    if not isinstance(message, bytes):
        raise TypeError(
            "Message must be bytes"
        )

    if len(message) != 32:
        raise ValueError(
            "Message must contain exactly 32 bytes"
        )

    if not isinstance(randomness, bytes):
        raise TypeError(
            "Randomness must be bytes"
        )

    if len(randomness) != 32:
        raise ValueError(
            "Randomness must contain exactly 32 bytes"
        )

    validate_k(k)
    validate_compression_parameters(du, dv)

    if eta1 not in (2, 3):
        raise ValueError("eta1 must be 2 or 3")

    if eta2 not in (2, 3):
        raise ValueError("eta2 must be 2 or 3")

    expected_key_length = 384 * k + 32

    if len(ek_pke) != expected_key_length:
        raise ValueError(
            "Invalid encryption key length"
        )

    # Step 1: Decode public vector t_hat

    t_hat = decode_vector(
        ek_pke[:384 * k],
        k,
        12
    )

    # Step 2: Extract rho

    rho = ek_pke[384 * k:]

    # Step 3: Generate A_hat and transpose

    a_hat = expand_a(
        rho,
        k
    )

    a_hat_transpose = transpose_matrix(
        a_hat
    )

    # Step 4: Generate y

    y = []

    nonce = 0

    for _ in range(k):

        random_bytes = PRF(
            randomness,
            nonce,
            eta1
        )

        polynomial = sample_poly_cbd(
            random_bytes,
            eta1
        )

        y.append(polynomial)

        nonce += 1

    # Step 5: Generate e1

    e1 = []

    for _ in range(k):

        random_bytes = PRF(
            randomness,
            nonce,
            eta2
        )

        polynomial = sample_poly_cbd(
            random_bytes,
            eta2
        )

        e1.append(polynomial)

        nonce += 1

    # Step 6: Generate e2

    random_bytes = PRF(
        randomness,
        nonce,
        eta2
    )

    e2 = sample_poly_cbd(
        random_bytes,
        eta2
    )

    # Step 7: Apply NTT to y

    y_hat = [
        ntt(polynomial)
        for polynomial in y
    ]

    # Step 8: Calculate u

    u_hat = matrix_vector_multiply_ntt(
        a_hat_transpose,
        y_hat
    )

    u = []

    for i in range(k):

        polynomial = inverse_ntt(
            u_hat[i]
        )

        polynomial = add_polynomials(
            polynomial,
            e1[i]
        )

        u.append(polynomial)

    # Step 9: Decode message

    message_values = byte_decode(
        message,
        1
    )

    mu = [
        decompress(value, 1)
        for value in message_values
    ]

    # Step 10: Calculate v

    v_hat = polynomial_vector_dot_ntt(
        t_hat,
        y_hat
    )

    v = inverse_ntt(v_hat)

    v = add_polynomials(
        v,
        e2
    )

    v = add_polynomials(
        v,
        mu
    )

    # Step 11: Compress and encode u and v

    c1 = encode_compressed_vector(
        u,
        du
    )

    c2 = encode_compressed_vector(
        [v],
        dv
    )

    # Step 12: Return ciphertext

    return c1 + c2


# ============================================================
# K-PKE.Decrypt
# FIPS 203 - Algorithm 15
# ============================================================

def k_pke_decrypt(
    dk_pke,
    ciphertext,
    k,
    du,
    dv
):

    # Validate inputs

    if not isinstance(dk_pke, bytes):
        raise TypeError(
            "Decryption key must be bytes"
        )

    if not isinstance(ciphertext, bytes):
        raise TypeError(
            "Ciphertext must be bytes"
        )

    validate_k(k)
    validate_compression_parameters(du, dv)

    # Step 1: Calculate expected lengths

    dk_length = 384 * k

    u_length = 32 * du * k

    v_length = 32 * dv

    ciphertext_length = u_length + v_length

    # Step 2: Validate lengths

    if len(dk_pke) != dk_length:
        raise ValueError(
            "Invalid decryption key length"
        )

    if len(ciphertext) != ciphertext_length:
        raise ValueError(
            "Invalid ciphertext length"
        )

    # Step 3: Decode u and v

    u_bytes = ciphertext[:u_length]

    v_bytes = ciphertext[u_length:]

    u_compressed = decode_vector(
        u_bytes,
        k,
        du
    )

    v_compressed = byte_decode(
        v_bytes,
        dv
    )

    # Step 4: Decompress u and v

    u = decompress_vector(
        u_compressed,
        du
    )

    v = [
        decompress(value, dv)
        for value in v_compressed
    ]

    # Step 5: Decode secret vector s_hat

    s_hat = decode_vector(
        dk_pke,
        k,
        12
    )

    # Step 6: Apply NTT to u

    u_hat = [
        ntt(polynomial)
        for polynomial in u
    ]

    # Step 7: Calculate s_hat transpose * u_hat

    product = polynomial_vector_dot_ntt(
        s_hat,
        u_hat
    )

    # Step 8: Apply inverse NTT

    product = inverse_ntt(
        product
    )

    # Step 9: Calculate w = v - product

    w = subtract_polynomials(
        v,
        product
    )

    # Step 10: Compress each coefficient

    message_bits = [
        compress(value, 1)
        for value in w
    ]

    # Step 11: Encode the original message

    message = byte_encode(
        message_bits,
        1
    )

    return message