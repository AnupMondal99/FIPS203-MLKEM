import pytest

from backend.core.k_pke import (
    k_pke_keygen,
    k_pke_encrypt
)


PARAMETERS = [
    (2, 3, 2, 10, 4, 768),
    (3, 2, 2, 10, 4, 1088),
    (4, 2, 2, 11, 5, 1568)
]


@pytest.mark.parametrize(
    "k,eta1,eta2,du,dv,expected_length",
    PARAMETERS
)
def test_encryption_ciphertext_length(
    k, eta1, eta2, du, dv, expected_length
):

    seed = bytes([1] * 32)

    message = bytes([2] * 32)

    randomness = bytes([3] * 32)

    ek, dk = k_pke_keygen(seed, k, eta1)

    ciphertext = k_pke_encrypt(
        ek,
        message,
        randomness,
        k,
        eta1,
        eta2,
        du,
        dv
    )

    assert len(ciphertext) == expected_length


def test_encryption_deterministic():

    seed = bytes([1] * 32)

    message = bytes([2] * 32)

    randomness = bytes([3] * 32)

    ek, _ = k_pke_keygen(seed, 2, 3)

    c1 = k_pke_encrypt(
        ek, message, randomness,
        2, 3, 2, 10, 4
    )

    c2 = k_pke_encrypt(
        ek, message, randomness,
        2, 3, 2, 10, 4
    )

    assert c1 == c2


def test_encryption_different_randomness():

    seed = bytes([1] * 32)

    message = bytes([2] * 32)

    ek, _ = k_pke_keygen(seed, 2, 3)

    c1 = k_pke_encrypt(
        ek, message, bytes([3] * 32),
        2, 3, 2, 10, 4
    )

    c2 = k_pke_encrypt(
        ek, message, bytes([4] * 32),
        2, 3, 2, 10, 4
    )

    assert c1 != c2


def test_encryption_invalid_message():

    ek, _ = k_pke_keygen(bytes(32), 2, 3)

    with pytest.raises(ValueError):

        k_pke_encrypt(
            ek, bytes(16), bytes(32),
            2, 3, 2, 10, 4
        )