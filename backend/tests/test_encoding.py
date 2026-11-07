import pytest

from backend.core.encoding import (
    N,
    Q,
    byte_encode,
    byte_decode,
    compress,
    decompress
)


# Test 1: ByteEncode output length

def test_byte_encode_length():

    poly = [0] * N

    result = byte_encode(poly, 12)

    assert len(result) == 384


# Test 2: ByteEncode and ByteDecode round trip

def test_encoding_round_trip():

    poly = [i % Q for i in range(N)]

    encoded = byte_encode(poly, 12)

    decoded = byte_decode(encoded, 12)

    assert decoded == poly


# Test 3: d = 1 round trip

def test_encoding_d1():

    poly = [i % 2 for i in range(N)]

    encoded = byte_encode(poly, 1)

    decoded = byte_decode(encoded, 1)

    assert decoded == poly


# Test 4: d = 4 round trip

def test_encoding_d4():

    poly = [i % 16 for i in range(N)]

    encoded = byte_encode(poly, 4)

    decoded = byte_decode(encoded, 4)

    assert decoded == poly


# Test 5: d = 10 round trip

def test_encoding_d10():

    poly = [i % 1024 for i in range(N)]

    encoded = byte_encode(poly, 10)

    decoded = byte_decode(encoded, 10)

    assert decoded == poly


# Test 6: d = 11 round trip

def test_encoding_d11():

    poly = [i % 2048 for i in range(N)]

    encoded = byte_encode(poly, 11)

    decoded = byte_decode(encoded, 11)

    assert decoded == poly


# Test 7: Invalid d

def test_invalid_d():

    with pytest.raises(ValueError):

        byte_encode([0] * N, 13)


# Test 8: Invalid polynomial length

def test_invalid_polynomial_length():

    with pytest.raises(ValueError):

        byte_encode([0, 1, 2], 12)


# Test 9: Invalid coefficient

def test_invalid_coefficient():

    poly = [0] * N

    poly[0] = Q

    with pytest.raises(ValueError):

        byte_encode(poly, 12)


# Test 10: Invalid byte length

def test_invalid_byte_length():

    with pytest.raises(ValueError):

        byte_decode(bytes(10), 12)


# Test 11: Compress output range

def test_compress_range():

    for value in range(Q):

        result = compress(value, 10)

        assert 0 <= result < 1024


# Test 12: Decompress output range

def test_decompress_range():

    for value in range(1024):

        result = decompress(value, 10)

        assert 0 <= result < Q


# Test 13: Compress-Decompress property

def test_compress_decompress_property():

    for d in range(1, 12):

        for value in range(1 << d):

            result = compress(decompress(value, d), d)

            assert result == value


# Test 14: Invalid compression input

def test_invalid_compress():

    with pytest.raises(ValueError):

        compress(3329, 10)


# Test 15: Invalid decompression input

def test_invalid_decompress():

    with pytest.raises(ValueError):

        decompress(1024, 10)
        
        # Test 16: Reject invalid 12-bit coefficient
def test_byte_decode_rejects_invalid_12bit_value():
    data = bytearray(384)

    # Encode 3329 (0xD01) manually into the first 12 bits
    data[0] = 0x01
    data[1] = 0x0D

    with pytest.raises(ValueError):
        byte_decode(bytes(data), 12)


# Test 17: Valid 12-bit coefficient

def test_byte_decode_valid_12bit_value():

    poly = [3328] + [0] * 255

    encoded = byte_encode(poly, 12)

    decoded = byte_decode(encoded, 12)

    assert decoded == poly