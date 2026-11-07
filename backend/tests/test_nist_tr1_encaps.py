import json
from pathlib import Path

import pytest

from backend.core.ml_kem import ml_kem_encaps_internal


BASE_DIR = (
    Path(__file__).resolve().parents[2]
    / "documentation"
    / "ACVP-Server"
    / "gen-val"
    / "json-files"
    / "ML-KEM-encapDecap-FIPS203-tr1"
)


def load_json(filename):
    with open(BASE_DIR / filename, "r") as file:
        return json.load(file)


prompt_data = load_json("prompt.json")
expected_data = load_json("expectedResults.json")


PARAMETERS = {
    "ML-KEM-512": (2, 3, 2, 10, 4),
    "ML-KEM-768": (3, 2, 2, 10, 4),
    "ML-KEM-1024": (4, 2, 2, 11, 5),
}


prompt_groups = {
    group["tgId"]: group
    for group in prompt_data["testGroups"]
}

expected_groups = {
    group["tgId"]: group
    for group in expected_data["testGroups"]
}


TEST_CASES = []

for group_id in [1, 2, 3]:

    prompt_group = prompt_groups[group_id]
    expected_group = expected_groups[group_id]

    parameter_set = prompt_group["parameterSet"]

    for prompt_test, expected_test in zip(
        prompt_group["tests"],
        expected_group["tests"]
    ):

        assert prompt_test["tcId"] == expected_test["tcId"]

        TEST_CASES.append(
            (parameter_set, prompt_test, expected_test)
        )


@pytest.mark.parametrize(
    "parameter_set,prompt,expected",
    TEST_CASES
)
def test_nist_tr1_encapsulation(parameter_set, prompt, expected):

    k, eta1, eta2, du, dv = PARAMETERS[parameter_set]

    ek = bytes.fromhex(prompt["ek"])
    m = bytes.fromhex(prompt["m"])

    expected_ciphertext = bytes.fromhex(expected["c"])
    expected_shared_secret = bytes.fromhex(expected["k"])

    actual_shared_secret, actual_ciphertext = ml_kem_encaps_internal(
        ek=ek,
        m=m,
        k=k,
        eta1=eta1,
        eta2=eta2,
        du=du,
        dv=dv
    )

    assert actual_ciphertext == expected_ciphertext, (
        f"{parameter_set} tcId={prompt['tcId']}: "
        "Ciphertext mismatch"
    )

    assert actual_shared_secret == expected_shared_secret, (
        f"{parameter_set} tcId={prompt['tcId']}: "
        "Shared secret mismatch"
    )