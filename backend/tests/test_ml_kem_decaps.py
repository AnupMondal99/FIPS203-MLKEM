import pytest

from backend.core.ml_kem import (
    ml_kem_keygen,
    ml_kem_encaps,
    ml_kem_decaps
)


@pytest.mark.parametrize(
    "k, eta1, eta2, du, dv",
    [
        (2, 3, 2, 10, 4),
        (3, 2, 2, 10, 4),
        (4, 2, 2, 11, 5),
    ]
)
def test_ml_kem_decaps_round_trip(
    k, eta1, eta2, du, dv
):

    ek, dk = ml_kem_keygen(k, eta1)

    sender_secret, ciphertext = ml_kem_encaps(
        ek, k, eta1, eta2, du, dv
    )

    receiver_secret = ml_kem_decaps(
        dk, ciphertext, k, eta1, eta2, du, dv
    )

    assert sender_secret == receiver_secret
    assert len(receiver_secret) == 32


def test_ml_kem_decaps_implicit_rejection():

    k, eta1, eta2, du, dv = 2, 3, 2, 10, 4

    ek, dk = ml_kem_keygen(k, eta1)

    sender_secret, ciphertext = ml_kem_encaps(
        ek, k, eta1, eta2, du, dv
    )

    modified_ciphertext = bytearray(ciphertext)
    modified_ciphertext[0] ^= 0x01

    receiver_secret = ml_kem_decaps(
        dk,
        bytes(modified_ciphertext),
        k, eta1, eta2, du, dv
    )

    assert receiver_secret != sender_secret
    assert len(receiver_secret) == 32


def test_ml_kem_decaps_invalid_key_length():

    with pytest.raises(ValueError):

        ml_kem_decaps(
            b"invalid",
            bytes(768),
            2, 3, 2, 10, 4
        )


def test_ml_kem_decaps_invalid_ciphertext_length():

    ek, dk = ml_kem_keygen(2, 3)

    with pytest.raises(ValueError):

        ml_kem_decaps(
            dk,
            b"invalid",
            2, 3, 2, 10, 4
        )


def test_ml_kem_decaps_invalid_key_hash():

    ek, dk = ml_kem_keygen(2, 3)

    corrupted_key = bytearray(dk)

    corrupted_key[768 * 2 + 32] ^= 0x01

    with pytest.raises(ValueError):

        ml_kem_decaps(
            bytes(corrupted_key),
            bytes(768),
            2, 3, 2, 10, 4
        )