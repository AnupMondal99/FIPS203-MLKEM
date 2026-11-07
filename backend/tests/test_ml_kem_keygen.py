import pytest

from backend.core.ml_kem import (
    ml_kem_keygen,
    ml_kem_keygen_internal
)


@pytest.mark.parametrize(
    "k, eta1, expected_ek, expected_dk",
    [
        (2, 3, 800, 1632),
        (3, 2, 1184, 2400),
        (4, 2, 1568, 3168),
    ]
)
def test_ml_kem_keygen_lengths(
    k,
    eta1,
    expected_ek,
    expected_dk
):

    ek, dk = ml_kem_keygen(k, eta1)

    assert len(ek) == expected_ek
    assert len(dk) == expected_dk


def test_ml_kem_keygen_internal_deterministic():

    d = bytes(range(32))
    z = bytes(range(32, 64))

    ek1, dk1 = ml_kem_keygen_internal(
        d, z, 2, 3
    )

    ek2, dk2 = ml_kem_keygen_internal(
        d, z, 2, 3
    )

    assert ek1 == ek2
    assert dk1 == dk2


def test_ml_kem_keygen_different_keys():

    ek1, dk1 = ml_kem_keygen(2, 3)

    ek2, dk2 = ml_kem_keygen(2, 3)

    assert ek1 != ek2
    assert dk1 != dk2


def test_ml_kem_keygen_invalid_k():

    with pytest.raises(ValueError):
        ml_kem_keygen(5, 3)


def test_ml_kem_keygen_invalid_eta():

    with pytest.raises(ValueError):
        ml_kem_keygen(2, 5)


def test_ml_kem_keygen_internal_invalid_seed():

    with pytest.raises(ValueError):
        ml_kem_keygen_internal(
            b"short",
            bytes(32),
            2,
            3
        )