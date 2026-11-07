import pytest

from backend.core.ntt import (
    N,
    Q,
    ntt,
    inverse_ntt,
    bit_reverse_7,
    get_zeta
)


def test_bit_reverse():

    assert bit_reverse_7(1) == 64

    assert bit_reverse_7(2) == 32

    assert bit_reverse_7(3) == 96


def test_zeta_calculation():

    assert get_zeta(1) == pow(17, 64, Q)

    assert get_zeta(2) == pow(17, 32, Q)


def test_ntt_output_length():

    poly = [0] * N

    transformed = ntt(poly)

    assert len(transformed) == N


def test_ntt_zero_polynomial():

    poly = [0] * N

    transformed = ntt(poly)

    assert transformed == [0] * N


def test_inverse_ntt_zero_polynomial():

    poly = [0] * N

    result = inverse_ntt(poly)

    assert result == [0] * N


def test_ntt_inverse_round_trip():

    poly = [
        (i * i + 7 * i + 13) % Q
        for i in range(N)
    ]

    transformed = ntt(poly)

    recovered = inverse_ntt(transformed)

    assert recovered == poly


def test_ntt_inverse_single_coefficient():

    poly = [0] * N

    poly[0] = 123

    transformed = ntt(poly)

    recovered = inverse_ntt(transformed)

    assert recovered == poly


def test_ntt_invalid_length():

    with pytest.raises(ValueError):

        ntt([1, 2, 3])


def test_ntt_invalid_coefficient():

    poly = [0] * N

    poly[0] = Q

    with pytest.raises(ValueError):

        ntt(poly)