import secrets
import hmac
import pytest

from backend.core.ml_kem import (
    ml_kem_keygen,
    ml_kem_keygen_internal,
    ml_kem_encaps,
    ml_kem_encaps_internal
)

from backend.core.k_pke import (
    k_pke_keygen,
    k_pke_encrypt,
    k_pke_decrypt,
    decode_vector
)

from backend.core.hashing import G, H, J

@pytest.mark.parametrize(
    "k, eta1, eta2, du, dv, expected_ciphertext",
    [
        (2, 3, 2, 10, 4, 768),
        (3, 2, 2, 10, 4, 1088),
        (4, 2, 2, 11, 5, 1568),
    ]
)
def test_ml_kem_encaps_lengths(
    k,
    eta1,
    eta2,
    du,
    dv,
    expected_ciphertext
):

    ek, dk = ml_kem_keygen(k, eta1)

    shared_secret, ciphertext = ml_kem_encaps(
        ek,
        k,
        eta1,
        eta2,
        du,
        dv
    )

    assert len(shared_secret) == 32

    assert len(ciphertext) == expected_ciphertext


def test_ml_kem_encaps_internal_deterministic():

    d = bytes(range(32))
    z = bytes(range(32, 64))
    m = bytes(range(64, 96))

    ek, dk = ml_kem_keygen_internal(
        d,
        z,
        2,
        3
    )

    K1, c1 = ml_kem_encaps_internal(
        ek, m, 2, 3, 2, 10, 4
    )

    K2, c2 = ml_kem_encaps_internal(
        ek, m, 2, 3, 2, 10, 4
    )

    assert K1 == K2
    assert c1 == c2


def test_ml_kem_encaps_different_randomness():

    ek, dk = ml_kem_keygen(2, 3)

    K1, c1 = ml_kem_encaps(
        ek, 2, 3, 2, 10, 4
    )

    K2, c2 = ml_kem_encaps(
        ek, 2, 3, 2, 10, 4
    )

    assert K1 != K2
    assert c1 != c2


def test_ml_kem_encaps_invalid_key_type():

    with pytest.raises(TypeError):

        ml_kem_encaps(
            "invalid",
            2,
            3,
            2,
            10,
            4
        )


def test_ml_kem_encaps_invalid_key_length():

    with pytest.raises(ValueError):

        ml_kem_encaps(
            b"invalid",
            2,
            3,
            2,
            10,
            4
        )


def test_ml_kem_encaps_internal_invalid_randomness():

    ek, dk = ml_kem_keygen(2, 3)

    with pytest.raises(ValueError):

        ml_kem_encaps_internal(
            ek,
            b"short",
            2,
            3,
            2,
            10,
            4
        )
        
        # ============================================================
# ML-KEM.Decaps_internal
# FIPS 203 - Algorithm 18
# ============================================================

def ml_kem_decaps_internal(
    dk,
    ciphertext,
    k,
    eta1,
    eta2,
    du,
    dv
):
    """
    ML-KEM.Decaps_internal

    Input:
        dk: ML-KEM decapsulation key
        ciphertext: Received ciphertext
        k: Module dimension
        eta1, eta2: Noise parameters
        du, dv: Compression parameters

    Output:
        32-byte shared secret
    """

    # Step 1: Validate basic inputs

    if not isinstance(dk, bytes):
        raise TypeError("Decapsulation key must be bytes")

    if not isinstance(ciphertext, bytes):
        raise TypeError("Ciphertext must be bytes")

    if k not in (2, 3, 4):
        raise ValueError("Invalid k value")

    if eta1 not in (2, 3) or eta2 not in (2, 3):
        raise ValueError("Invalid eta values")

    if du not in (10, 11) or dv not in (4, 5):
        raise ValueError("Invalid compression parameters")

    # Step 2: Extract key components

    dk_pke_length = 384 * k

    ek_pke_length = 384 * k + 32

    expected_dk_length = 768 * k + 96

    if len(dk) != expected_dk_length:
        raise ValueError("Invalid decapsulation key length")

    expected_ciphertext_length = 32 * (du * k + dv)

    if len(ciphertext) != expected_ciphertext_length:
        raise ValueError("Invalid ciphertext length")

    dk_pke = dk[:dk_pke_length]

    ek_pke = dk[
        dk_pke_length:
        dk_pke_length + ek_pke_length
    ]

    h = dk[
        768 * k + 32:
        768 * k + 64
    ]

    z = dk[
        768 * k + 64:
        768 * k + 96
    ]

    # Step 3: Decrypt ciphertext

    m_prime = k_pke_decrypt(
        dk_pke,
        ciphertext,
        k,
        du,
        dv
    )

    # Step 4: Generate candidate shared secret and randomness

    output = G(
        m_prime + h
    )

    K_prime = output[:32]

    r_prime = output[32:64]

    # Step 5: Generate implicit rejection secret

    K_bar = J(
        z + ciphertext
    )

    # Step 6: Re-encrypt decrypted message

    ciphertext_prime = k_pke_encrypt(
        ek_pke,
        m_prime,
        r_prime,
        k,
        eta1,
        eta2,
        du,
        dv
    )

    # Step 7: Compare ciphertexts

    if not hmac.compare_digest(
        ciphertext,
        ciphertext_prime
    ):

        # Implicit rejection

        K_prime = K_bar

    # Step 8: Return shared secret

    return K_prime


# ============================================================
# ML-KEM.Decaps
# FIPS 203 - Algorithm 21
# ============================================================

def ml_kem_decaps(
    dk,
    ciphertext,
    k,
    eta1,
    eta2,
    du,
    dv
):
    """
    ML-KEM.Decaps

    Input:
        dk: Checked ML-KEM decapsulation key
        ciphertext: Received ciphertext

    Output:
        32-byte shared secret
    """

    # Step 1: Validate input types

    if not isinstance(dk, bytes):
        raise TypeError("Decapsulation key must be bytes")

    if not isinstance(ciphertext, bytes):
        raise TypeError("Ciphertext must be bytes")

    if k not in (2, 3, 4):
        raise ValueError("Invalid k value")

    if eta1 not in (2, 3) or eta2 not in (2, 3):
        raise ValueError("Invalid eta values")

    if du not in (10, 11) or dv not in (4, 5):
        raise ValueError("Invalid compression parameters")

    # Step 2: Validate decapsulation key length

    expected_dk_length = 768 * k + 96

    if len(dk) != expected_dk_length:
        raise ValueError("Invalid decapsulation key length")

    # Step 3: Validate ciphertext length

    expected_ciphertext_length = 32 * (du * k + dv)

    if len(ciphertext) != expected_ciphertext_length:
        raise ValueError("Invalid ciphertext length")

    # Step 4: Extract encapsulation key and stored hash

    ek_start = 384 * k

    ek_end = 768 * k + 32

    ek_pke = dk[ek_start:ek_end]

    stored_hash = dk[
        768 * k + 32:
        768 * k + 64
    ]

    # Step 5: Verify encapsulation key hash

    calculated_hash = H(ek_pke)

    if not hmac.compare_digest(
        calculated_hash,
        stored_hash
    ):
        raise ValueError(
            "Decapsulation key hash verification failed"
        )

    # Step 6: Perform internal decapsulation

    shared_secret = ml_kem_decaps_internal(
        dk,
        ciphertext,
        k,
        eta1,
        eta2,
        du,
        dv
    )

    # Step 7: Return shared secret

    return shared_secret