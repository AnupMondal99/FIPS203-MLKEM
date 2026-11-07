import json
from pathlib import Path

import pytest

from backend.core.ml_kem import ml_kem_keygen_internal


BASE_DIR = (
    Path(__file__).resolve().parents[2]
    / "documentation"
    / "ACVP-Server"
    / "gen-val"
    / "json-files"
    / "ML-KEM-keyGen-FIPS203"
)


def load_json(filename):
    with open(BASE_DIR / filename, "r") as file:
        return json.load(file)


prompt_data = load_json("prompt.json")
expected_data = load_json("expectedResults.json")


PARAMETERS = {
    "ML-KEM-512": (2, 3),
    "ML-KEM-768": (3, 2),
    "ML-KEM-1024": (4, 2),
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

for group_id, prompt_group in prompt_groups.items():

    expected_group = expected_groups[group_id]

    parameter_set = prompt_group["parameterSet"]

    for prompt_test, expected_test in zip(
        prompt_group["tests"],
        expected_group["tests"]
    ):

        assert prompt_test["tcId"] == expected_test["tcId"]

        TEST_CASES.append(
            (
                parameter_set,
                prompt_test,
                expected_test
            )
        )


@pytest.mark.parametrize(
    "parameter_set,prompt,expected",
    TEST_CASES
)
def test_nist_keygen(parameter_set, prompt, expected):

    k, eta1 = PARAMETERS[parameter_set]

    d = bytes.fromhex(prompt["d"])
    z = bytes.fromhex(prompt["z"])

    expected_ek = bytes.fromhex(expected["ek"])
    expected_dk = bytes.fromhex(expected["dk"])

    actual_ek, actual_dk = ml_kem_keygen_internal(
        d=d,
        z=z,
        k=k,
        eta1=eta1
    )

    assert actual_ek == expected_ek, (
        f"{parameter_set} tcId={prompt['tcId']}: "
        "Encapsulation key mismatch"
    )

    assert actual_dk == expected_dk, (
        f"{parameter_set} tcId={prompt['tcId']}: "
        "Decapsulation key mismatch"
    )