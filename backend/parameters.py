"""
FIPS 203 - ML-KEM Parameter Configuration

Supported parameter sets:
1. ML-KEM-512
2. ML-KEM-768
3. ML-KEM-1024
"""

PARAMETER_SETS = {

    "ML-KEM-512": {
        "n": 256,
        "q": 3329,
        "k": 2,
        "eta1": 3,
        "eta2": 2,
        "du": 10,
        "dv": 4,
        "security_category": 1,
        "ek_size": 800,
        "dk_size": 1632,
        "ciphertext_size": 768,
        "shared_secret_size": 32
    },

    "ML-KEM-768": {
        "n": 256,
        "q": 3329,
        "k": 3,
        "eta1": 2,
        "eta2": 2,
        "du": 10,
        "dv": 4,
        "security_category": 3,
        "ek_size": 1184,
        "dk_size": 2400,
        "ciphertext_size": 1088,
        "shared_secret_size": 32
    },

    "ML-KEM-1024": {
        "n": 256,
        "q": 3329,
        "k": 4,
        "eta1": 2,
        "eta2": 2,
        "du": 11,
        "dv": 5,
        "security_category": 5,
        "ek_size": 1568,
        "dk_size": 3168,
        "ciphertext_size": 1568,
        "shared_secret_size": 32
    }

}


def get_parameters(parameter_name):

    if parameter_name not in PARAMETER_SETS:

        raise ValueError(
            f"Invalid parameter set: {parameter_name}"
        )

    return PARAMETER_SETS[parameter_name]


def display_parameters(parameter_name):

    parameters = get_parameters(parameter_name)

    print(f"\nSelected Parameter: {parameter_name}")

    print("-" * 40)

    for key, value in parameters.items():

        print(f"{key:25} : {value}")


if __name__ == "__main__":

    for parameter in PARAMETER_SETS:

        display_parameters(parameter)