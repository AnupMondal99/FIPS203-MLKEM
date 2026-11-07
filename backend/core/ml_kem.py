"""
FIPS 203 - ML-KEM

Algorithm 16: ML-KEM.KeyGen_internal
Algorithm 17: ML-KEM.Encaps_internal
Algorithm 18: ML-KEM.Decaps_internal
Algorithm 19: ML-KEM.KeyGen
Algorithm 20: ML-KEM.Encaps
Algorithm 21: ML-KEM.Decaps
"""

import secrets
import hmac

from backend.core.k_pke import (
    k_pke_keygen,
    k_pke_encrypt,
    k_pke_decrypt,
    decode_vector
)

from backend.core.hashing import G, H, J


# ============================================================
# ML-KEM Parameter Validation
# ============================================================

def validate_parameters(k, eta1, eta2, du, dv):

    if not isinstance(k, int) or isinstance(k, bool):
        raise TypeError("k must be an integer")

    if k not in (2, 3, 4):
        raise ValueError("k must be 2, 3, or 4")

    if not isinstance(eta1, int) or isinstance(eta1, bool):
        raise TypeError("eta1 must be an integer")

    if not isinstance(eta2, int) or isinstance(eta2, bool):
        raise TypeError("eta2 must be an integer")

    if not isinstance(du, int) or isinstance(du, bool):
        raise TypeError("du must be an integer")

    if not isinstance(dv, int) or isinstance(dv, bool):
        raise TypeError("dv must be an integer")

    expected_parameters = {
        2: (3, 2, 10, 4),
        3: (2, 2, 10, 4),
        4: (2, 2, 11, 5)
    }

    actual_parameters = (eta1, eta2, du, dv)

    if actual_parameters != expected_parameters[k]:
        raise ValueError(
            "Invalid ML-KEM parameter combination"
        )


# ============================================================
# Encapsulation Key Validation
# ============================================================

def validate_encapsulation_key(ek, k):

    if not isinstance(ek, bytes):
        raise TypeError(
            "Encapsulation key must be bytes"
        )

    expected_length = 384 * k + 32

    if len(ek) != expected_length:
        raise ValueError(
            "Invalid encapsulation key length"
        )

    # Validate the encoded public polynomial vector.
    # ByteDecode12 rejects coefficients >= 3329.

    decode_vector(
        ek[:384 * k],
        k,
        12
    )

    return True


# ============================================================
# Decapsulation Key Validation
# ============================================================

def validate_decapsulation_key(dk, k):

    if not isinstance(dk, bytes):
        raise TypeError(
            "Decapsulation key must be bytes"
        )

    expected_length = 768 * k + 96

    if len(dk) != expected_length:
        raise ValueError(
            "Invalid decapsulation key length"
        )

    # Extract the encapsulation key from dk.

    ek_start = 384 * k
    ek_end = 768 * k + 32

    ek = dk[ek_start:ek_end]

    # Extract the stored hash.

    stored_hash = dk[
        768 * k + 32:
        768 * k + 64
    ]

    # Verify H(ek).

    calculated_hash = H(ek)

    if not hmac.compare_digest(
        calculated_hash,
        stored_hash
    ):
        raise ValueError(
            "Decapsulation key hash verification failed"
        )

    # Validate the embedded encapsulation key.

    validate_encapsulation_key(
        ek,
        k
    )

    return True


# ============================================================
# ML-KEM.KeyGen_internal
# FIPS 203 - Algorithm 16
# ============================================================

def ml_kem_keygen_internal(d, z, k, eta1):

    # Step 1: Validate inputs.

    if not isinstance(d, bytes):
        raise TypeError("Seed d must be bytes")

    if not isinstance(z, bytes):
        raise TypeError("Seed z must be bytes")

    if len(d) != 32:
        raise ValueError(
            "Seed d must contain exactly 32 bytes"
        )

    if len(z) != 32:
        raise ValueError(
            "Seed z must contain exactly 32 bytes"
        )

    if not isinstance(k, int) or isinstance(k, bool):
        raise TypeError("k must be an integer")

    if k not in (2, 3, 4):
        raise ValueError("Invalid k value")

    if eta1 != (3 if k == 2 else 2):
        raise ValueError("Invalid eta1 for this parameter set")

    # Step 2: Generate K-PKE key pair.

    ek_pke, dk_pke = k_pke_keygen(
        d,
        k,
        eta1
    )

    # Step 3: Set encapsulation key.

    ek = ek_pke

    # Step 4: Calculate H(ek).

    h_ek = H(ek)

    # Step 5: Construct decapsulation key.

    dk = (
        dk_pke
        + ek
        + h_ek
        + z
    )

    # Step 6: Return keys.

    return ek, dk


# ============================================================
# ML-KEM.KeyGen
# FIPS 203 - Algorithm 19
# ============================================================

def ml_kem_keygen(k, eta1):

    if not isinstance(k, int) or isinstance(k, bool):
        raise TypeError("k must be an integer")

    if k not in (2, 3, 4):
        raise ValueError("Invalid k value")

    if eta1 != (3 if k == 2 else 2):
        raise ValueError("Invalid eta1 for this parameter set")

    # Generate two independent random 32-byte values.

    d = secrets.token_bytes(32)
    z = secrets.token_bytes(32)

    # Generate the key pair internally.

    ek, dk = ml_kem_keygen_internal(
        d,
        z,
        k,
        eta1
    )

    return ek, dk


# ============================================================
# ML-KEM.Encaps_internal
# FIPS 203 - Algorithm 17
# ============================================================

def ml_kem_encaps_internal(
    ek,
    m,
    k,
    eta1,
    eta2,
    du,
    dv
):

    # Step 1: Validate parameters.

    validate_parameters(
        k,
        eta1,
        eta2,
        du,
        dv
    )

    # Step 2: Validate inputs.

    if not isinstance(m, bytes):
        raise TypeError("m must be bytes")

    if len(m) != 32:
        raise ValueError(
            "m must contain exactly 32 bytes"
        )

    # Step 3: Validate encapsulation key.

    validate_encapsulation_key(
        ek,
        k
    )

    # Step 4: Calculate G(m || H(ek)).

    output = G(
        m + H(ek)
    )

    # Step 5: Split output into K and r.

    K = output[:32]
    r = output[32:64]

    # Step 6: Encrypt m using K-PKE.

    ciphertext = k_pke_encrypt(
        ek,
        m,
        r,
        k,
        eta1,
        eta2,
        du,
        dv
    )

    # Step 7: Return shared secret and ciphertext.

    return K, ciphertext


# ============================================================
# ML-KEM.Encaps
# FIPS 203 - Algorithm 20
# ============================================================

def ml_kem_encaps(
    ek,
    k,
    eta1,
    eta2,
    du,
    dv
):

    # Step 1: Validate parameters.

    validate_parameters(
        k,
        eta1,
        eta2,
        du,
        dv
    )

    # Step 2: Validate encapsulation key.

    validate_encapsulation_key(
        ek,
        k
    )

    # Step 3: Generate random 32-byte message.

    m = secrets.token_bytes(32)

    if m is None:
        raise RuntimeError(
            "Random number generation failed"
        )

    # Step 4: Perform internal encapsulation.

    K, ciphertext = ml_kem_encaps_internal(
        ek,
        m,
        k,
        eta1,
        eta2,
        du,
        dv
    )

    # Step 5: Return shared secret and ciphertext.

    return K, ciphertext


# ============================================================
# ML-KEM.Decaps_internal
# FIPS 203 - Algorithm 18
# ============================================================

def ml_kem_decaps_internal(
    dk,
    ciphertext,
    k,
    eta1,
    eta2,
    du,
    dv
):

    # Step 1: Validate parameters.

    validate_parameters(
        k,
        eta1,
        eta2,
        du,
        dv
    )

    # Step 2: Validate basic input types.

    if not isinstance(dk, bytes):
        raise TypeError(
            "Decapsulation key must be bytes"
        )

    if not isinstance(ciphertext, bytes):
        raise TypeError(
            "Ciphertext must be bytes"
        )

    # Step 3: Extract key components.

    dk_pke_length = 384 * k
    ek_length = 384 * k + 32

    dk_pke = dk[:dk_pke_length]

    ek_start = dk_pke_length
    ek_end = ek_start + ek_length

    ek = dk[ek_start:ek_end]

    h = dk[
        768 * k + 32:
        768 * k + 64
    ]

    z = dk[
        768 * k + 64:
        768 * k + 96
    ]

    # Step 4: Decrypt ciphertext using K-PKE.

    m_prime = k_pke_decrypt(
        dk_pke,
        ciphertext,
        k,
        du,
        dv
    )

    # Step 5: Calculate G(m' || h).

    output = G(
        m_prime + h
    )

    K_prime = output[:32]
    r_prime = output[32:64]

    # Step 6: Calculate implicit rejection secret.

    K_bar = J(
        z + ciphertext
    )

    # Step 7: Re-encrypt m'.

    ciphertext_prime = k_pke_encrypt(
        ek,
        m_prime,
        r_prime,
        k,
        eta1,
        eta2,
        du,
        dv
    )

    # Step 8: Compare ciphertexts.

    if not hmac.compare_digest(
        ciphertext,
        ciphertext_prime
    ):

        # Implicit rejection.

        K_prime = K_bar

    # Step 9: Return shared secret.

    return K_prime


# ============================================================
# ML-KEM.Decaps
# FIPS 203 - Algorithm 21
# ============================================================

def ml_kem_decaps(
    dk,
    ciphertext,
    k,
    eta1,
    eta2,
    du,
    dv
):

    # Step 1: Validate parameters.

    validate_parameters(
        k,
        eta1,
        eta2,
        du,
        dv
    )

    # Step 2: Validate ciphertext type.

    if not isinstance(ciphertext, bytes):
        raise TypeError(
            "Ciphertext must be bytes"
        )

    # Step 3: Validate ciphertext length.

    expected_ciphertext_length = (
        32 * (du * k + dv)
    )

    if len(ciphertext) != expected_ciphertext_length:
        raise ValueError(
            "Invalid ciphertext length"
        )

    # Step 4: Validate decapsulation key.

    validate_decapsulation_key(
        dk,
        k
    )

    # Step 5: Perform internal decapsulation.

    shared_secret = ml_kem_decaps_internal(
        dk,
        ciphertext,
        k,
        eta1,
        eta2,
        du,
        dv
    )

    # Step 6: Return shared secret.

    return shared_secret