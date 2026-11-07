import pytest

from backend.core.cbd import (
    N,
    Q,
    bytes_to_bits,
    sample_poly_cbd
)


# Test 1: Bytes to bits conversion

def test_bytes_to_bits():

    result = bytes_to_bits([3])

    assert result == [1, 1, 0, 0, 0, 0, 0, 0]


# Test 2: Output length for eta = 2

def test_cbd_output_length_eta2():

    data = bytes(128)

    result = sample_poly_cbd(data, 2)

    assert len(result) == N


# Test 3: Output length for eta = 3

def test_cbd_output_length_eta3():

    data = bytes(192)

    result = sample_poly_cbd(data, 3)

    assert len(result) == N


# Test 4: Zero input

def test_cbd_zero_input():

    data = bytes(128)

    result = sample_poly_cbd(data, 2)

    assert result == [0] * N


# Test 5: Eta 2 exact coefficient test

def test_cbd_eta2_exact_values():

    data = bytes([3] * 128)

    result = sample_poly_cbd(data, 2)

    assert result == [2, 0] * 128


# Test 6: Coefficient range for eta 2

def test_cbd_coefficient_range_eta2():

    data = bytes([255] * 128)

    result = sample_poly_cbd(data, 2)

    allowed = {0, 1, 2, Q - 2, Q - 1}

    assert all(value in allowed for value in result)


# Test 7: Coefficient range for eta 3

def test_cbd_coefficient_range_eta3():

    data = bytes([255] * 192)

    result = sample_poly_cbd(data, 3)

    allowed = {
        0, 1, 2, 3,
        Q - 3, Q - 2, Q - 1
    }

    assert all(value in allowed for value in result)


# Test 8: Invalid eta

def test_cbd_invalid_eta():

    data = bytes(128)

    with pytest.raises(ValueError):

        sample_poly_cbd(data, 4)


# Test 9: Invalid input length

def test_cbd_invalid_input_length():

    data = bytes(100)

    with pytest.raises(ValueError):

        sample_poly_cbd(data, 2)


# Test 10: Invalid byte value

def test_cbd_invalid_byte():

    data = [256] + [0] * 127

    with pytest.raises(ValueError):

        sample_poly_cbd(data, 2)