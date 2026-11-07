import pytest

from backend.core.hashing import (
    H,
    G,
    PRF,
    XOF,
    J
)


# Test 1: H output length

def test_h_output_length():

    result = H(b"Hello ML-KEM")

    assert len(result) == 32


# Test 2: G output length

def test_g_output_length():

    result = G(b"Hello ML-KEM")

    assert len(result) == 64


# Test 3: PRF eta 2

def test_prf_eta2():

    seed = bytes(32)

    result = PRF(seed, 0, 2)

    assert len(result) == 128


# Test 4: PRF eta 3

def test_prf_eta3():

    seed = bytes(32)

    result = PRF(seed, 0, 3)

    assert len(result) == 192


# Test 5: PRF determinism

def test_prf_deterministic():

    seed = bytes([1] * 32)

    result1 = PRF(seed, 5, 2)

    result2 = PRF(seed, 5, 2)

    assert result1 == result2


# Test 6: PRF nonce changes output

def test_prf_nonce_changes_output():

    seed = bytes([1] * 32)

    result1 = PRF(seed, 1, 2)

    result2 = PRF(seed, 2, 2)

    assert result1 != result2


# Test 7: XOF output length

def test_xof_output_length():

    seed = bytes(32)

    result = XOF(seed, 0, 0, 128)

    assert len(result) == 128


# Test 8: XOF determinism

def test_xof_deterministic():

    seed = bytes([2] * 32)

    result1 = XOF(seed, 1, 2, 64)

    result2 = XOF(seed, 1, 2, 64)

    assert result1 == result2


# Test 9: J output length

def test_j_output_length():

    result = J(b"Hello ML-KEM")

    assert len(result) == 32


# Test 10: J determinism

def test_j_deterministic():

    result1 = J(b"ML-KEM")

    result2 = J(b"ML-KEM")

    assert result1 == result2


# Test 11: Invalid seed

def test_prf_invalid_seed():

    with pytest.raises(ValueError):

        PRF(bytes(16), 0, 2)


# Test 12: Invalid eta

def test_prf_invalid_eta():

    with pytest.raises(ValueError):

        PRF(bytes(32), 0, 4)


# Test 13: Invalid nonce

def test_prf_invalid_nonce():

    with pytest.raises(ValueError):

        PRF(bytes(32), 256, 2)


# Test 14: Invalid XOF coordinate

def test_xof_invalid_coordinate():

    with pytest.raises(ValueError):

        XOF(bytes(32), 256, 0, 64)


# Test 15: Negative XOF output length

def test_xof_negative_output_length():

    with pytest.raises(ValueError):

        XOF(bytes(32), 0, 0, -1)