import pytest

from backend.core.k_pke import (
    k_pke_keygen,
    k_pke_encrypt,
    k_pke_decrypt
)


@pytest.mark.parametrize(
    "k, eta1, eta2, du, dv",
    [
        (2, 3, 2, 10, 4),
        (3, 2, 2, 10, 4),
        (4, 2, 2, 11, 5),
    ]
)
def test_k_pke_decrypt_round_trip(
    k, eta1, eta2, du, dv
):

    d = bytes(range(32))
    randomness = bytes(range(32, 64))

    ek_pke, dk_pke = k_pke_keygen(
        d, k, eta1
    )

    message = bytes(range(32))

    ciphertext = k_pke_encrypt(
        ek_pke,
        message,
        randomness,
        k,
        eta1,
        eta2,
        du,
        dv
    )

    decrypted_message = k_pke_decrypt(
        dk_pke,
        ciphertext,
        k,
        du,
        dv
    )

    assert decrypted_message == message
    assert len(decrypted_message) == 32