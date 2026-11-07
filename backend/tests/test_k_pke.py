import pytest

from backend.core.k_pke import k_pke_keygen


# Test 1: ML-KEM-512 key sizes

def test_k_pke_keygen_512():

    seed = bytes(32)

    ek, dk = k_pke_keygen(seed, 2, 3)

    assert len(ek) == 800

    assert len(dk) == 768


# Test 2: ML-KEM-768 key sizes

def test_k_pke_keygen_768():

    seed = bytes(32)

    ek, dk = k_pke_keygen(seed, 3, 2)

    assert len(ek) == 1184

    assert len(dk) == 1152


# Test 3: ML-KEM-1024 key sizes

def test_k_pke_keygen_1024():

    seed = bytes(32)

    ek, dk = k_pke_keygen(seed, 4, 2)

    assert len(ek) == 1568

    assert len(dk) == 1536


# Test 4: Deterministic key generation

def test_keygen_deterministic():

    seed = bytes([5] * 32)

    ek1, dk1 = k_pke_keygen(seed, 2, 3)

    ek2, dk2 = k_pke_keygen(seed, 2, 3)

    assert ek1 == ek2

    assert dk1 == dk2


# Test 5: Different seeds produce different keys

def test_keygen_different_seeds():

    seed1 = bytes([1] * 32)

    seed2 = bytes([2] * 32)

    ek1, dk1 = k_pke_keygen(seed1, 2, 3)

    ek2, dk2 = k_pke_keygen(seed2, 2, 3)

    assert ek1 != ek2

    assert dk1 != dk2


# Test 6: Invalid seed length

def test_keygen_invalid_seed():

    with pytest.raises(ValueError):

        k_pke_keygen(bytes(16), 2, 3)


# Test 7: Invalid parameter k

def test_keygen_invalid_k():

    with pytest.raises(ValueError):

        k_pke_keygen(bytes(32), 5, 2)


# Test 8: Invalid eta1

def test_keygen_invalid_eta():

    with pytest.raises(ValueError):

        k_pke_keygen(bytes(32), 2, 4)


# Test 9: Invalid seed type

def test_keygen_invalid_seed_type():

    with pytest.raises(TypeError):

        k_pke_keygen("invalid", 2, 3)