import pytest

from backend.core.sampling import (
    N,
    Q,
    sample_ntt
)


# Test 1: Output length

def test_sample_ntt_output_length():

    seed = bytes(32)

    result = sample_ntt(seed, 0, 0)

    assert len(result) == N


# Test 2: Coefficient range

def test_sample_ntt_coefficient_range():

    seed = bytes([1] * 32)

    result = sample_ntt(seed, 0, 0)

    assert all(0 <= x < Q for x in result)


# Test 3: Deterministic output

def test_sample_ntt_deterministic():

    seed = bytes([5] * 32)

    result1 = sample_ntt(seed, 1, 2)

    result2 = sample_ntt(seed, 1, 2)

    assert result1 == result2


# Test 4: Different seed

def test_sample_ntt_different_seed():

    seed1 = bytes([1] * 32)

    seed2 = bytes([2] * 32)

    result1 = sample_ntt(seed1, 0, 0)

    result2 = sample_ntt(seed2, 0, 0)

    assert result1 != result2


# Test 5: Different indices

def test_sample_ntt_different_indices():

    seed = bytes([3] * 32)

    result1 = sample_ntt(seed, 0, 0)

    result2 = sample_ntt(seed, 1, 0)

    assert result1 != result2


# Test 6: Invalid seed length

def test_sample_ntt_invalid_seed():

    with pytest.raises(ValueError):

        sample_ntt(bytes(16), 0, 0)


# Test 7: Invalid index

def test_sample_ntt_invalid_index():

    seed = bytes(32)

    with pytest.raises(ValueError):

        sample_ntt(seed, 256, 0)


# Test 8: Invalid seed type

def test_sample_ntt_invalid_seed_type():

    with pytest.raises(TypeError):

        sample_ntt("invalid seed", 0, 0)


# Test 9: Invalid index type

def test_sample_ntt_invalid_index_type():

    seed = bytes(32)

    with pytest.raises(TypeError):

        sample_ntt(seed, "0", 0)