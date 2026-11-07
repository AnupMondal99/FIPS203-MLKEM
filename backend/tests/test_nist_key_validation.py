import json
from pathlib import Path

import pytest

from backend.core.ml_kem import (
    validate_encapsulation_key,
    validate_decapsulation_key,
)


BASE_DIR = (
    Path(__file__).resolve().parents[2]
    / "documentation"
    / "ACVP-Server"
    / "gen-val"
    / "json-files"
    / "ML-KEM-encapDecap-FIPS203"
)


def load_json(filename):
    with open(BASE_DIR / filename, "r") as file:
        return json.load(file)


prompt_data = load_json("prompt.json")
expected_data = load_json("expectedResults.json")


PARAMETERS = {
    "ML-KEM-512": 2,
    "ML-KEM-768": 3,
    "ML-KEM-1024": 4,
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

for group_id in range(7, 13):

    prompt_group = prompt_groups[group_id]
    expected_group = expected_groups[group_id]

    parameter_set = prompt_group["parameterSet"]
    key_type = "dk" if group_id % 2 == 1 else "ek"

    for prompt_test, expected_test in zip(
        prompt_group["tests"],
        expected_group["tests"]
    ):

        assert prompt_test["tcId"] == expected_test["tcId"]

        TEST_CASES.append(
            (
                parameter_set,
                key_type,
                prompt_test,
                expected_test
            )
        )


@pytest.mark.parametrize(
    "parameter_set,key_type,prompt,expected",
    TEST_CASES
)
def test_nist_key_validation(
    parameter_set,
    key_type,
    prompt,
    expected
):

    k = PARAMETERS[parameter_set]

    key = bytes.fromhex(prompt[key_type])

    should_pass = expected["testPassed"]

    validator = (
        validate_decapsulation_key
        if key_type == "dk"
        else validate_encapsulation_key
    )

    try:
        result = validator(key, k)
        actual_pass = result is True

    except (ValueError, TypeError):
        actual_pass = False

    assert actual_pass == should_pass, (
        f"{parameter_set} {key_type} "
        f"tcId={prompt['tcId']}: "
        f"Expected testPassed={should_pass}, "
        f"got {actual_pass}"
    )