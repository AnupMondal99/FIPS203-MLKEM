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
    / "ML-KEM-encapDecap-FIPS203-tr1"
)


def load_json(filename):
    with open(BASE_DIR / filename, "r") as file:
        return json.load(file)


prompt_data = load_json("prompt.json")
expected_data = load_json("expectedResults.json")

prompt_groups = {g["tgId"]: g for g in prompt_data["testGroups"]}
expected_groups = {g["tgId"]: g for g in expected_data["testGroups"]}

TEST_CASES = []

for group_id in range(10, 16):
    pg = prompt_groups[group_id]
    eg = expected_groups[group_id]

    for p, e in zip(pg["tests"], eg["tests"]):
        assert p["tcId"] == e["tcId"]
        TEST_CASES.append((group_id, pg["parameterSet"], p, e))


@pytest.mark.parametrize(
    "group_id,parameter_set,prompt,expected",
    TEST_CASES,
)
def test_nist_tr1_key_validation(
    group_id, parameter_set, prompt, expected
):
    k = {
        "ML-KEM-512": 2,
        "ML-KEM-768": 3,
        "ML-KEM-1024": 4,
    }[parameter_set]

    if "dk" in prompt:
        key = bytes.fromhex(prompt["dk"])
        validator = validate_decapsulation_key
    else:
        key = bytes.fromhex(prompt["ek"])
        validator = validate_encapsulation_key

    try:
        actual = validator(key, k)
    except (ValueError, TypeError):
        actual = False

    expected_result = expected["testPassed"]

    assert actual == expected_result, (
        f"Group {group_id}, {parameter_set}, "
        f"tcId={prompt['tcId']}: "
        f"Expected {expected_result}, got {actual}"
    )