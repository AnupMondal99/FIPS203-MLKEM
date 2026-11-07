import pytest

from backend.core.ntt import N, Q, ntt, inverse_ntt

from backend.core.polynomial import polynomial_multiply

from backend.core.ntt_multiplication import (
    base_case_multiply,
    multiply_ntts,
    get_gamma
)


# Test 1: BaseCaseMultiply

def test_base_case_multiply():

    result = base_case_multiply(
        2, 3,
        4, 5,
        6
    )

    expected_c0 = (2 * 4 + 3 * 5 * 6) % Q
    expected_c1 = (2 * 5 + 3 * 4) % Q

    assert result == (expected_c0, expected_c1)


# Test 2: BaseCaseMultiply modulo q

def test_base_case_modulo():

    result = base_case_multiply(
        3000, 3000,
        3000, 3000,
        3000
    )

    assert 0 <= result[0] < Q
    assert 0 <= result[1] < Q


# Test 3: Gamma calculation

def test_gamma_calculation():

    assert get_gamma(0) == pow(17, 1, Q)

    assert get_gamma(1) == pow(17, 129, Q)


# Test 4: Output length

def test_multiply_ntts_output_length():

    f_hat = [0] * N
    g_hat = [0] * N

    result = multiply_ntts(f_hat, g_hat)

    assert len(result) == N


# Test 5: Zero polynomial multiplication

def test_multiply_ntts_zero():

    f_hat = [0] * N
    g_hat = [0] * N

    result = multiply_ntts(f_hat, g_hat)

    assert result == [0] * N


# Test 6: Multiplication with one polynomial zero

def test_multiply_ntts_one_zero():

    f_hat = [0] * N

    g_hat = [i % Q for i in range(N)]

    result = multiply_ntts(f_hat, g_hat)

    assert result == [0] * N


# Test 7: NTT multiplication consistency

def test_ntt_multiplication_consistency():

    f = [(i + 3) % Q for i in range(N)]

    g = [(2 * i + 5) % Q for i in range(N)]

    f_hat = ntt(f)
    g_hat = ntt(g)

    h_hat = multiply_ntts(f_hat, g_hat)

    result = inverse_ntt(h_hat)

    expected = polynomial_multiply(f, g)

    assert result == expected


# Test 8: Invalid input length

def test_multiply_ntts_invalid_length():

    with pytest.raises(ValueError):

        multiply_ntts([1, 2, 3], [1, 2, 3])


# Test 9: Invalid coefficient

def test_multiply_ntts_invalid_coefficient():

    f_hat = [0] * N
    g_hat = [0] * N

    f_hat[0] = Q

    with pytest.raises(ValueError):

        multiply_ntts(f_hat, g_hat)


# Test 10: Negative coefficient

def test_multiply_ntts_negative_coefficient():

    f_hat = [0] * N
    g_hat = [0] * N

    f_hat[0] = -1

    with pytest.raises(ValueError):

        multiply_ntts(f_hat, g_hat)