#!/usr/bin/env python3

# pytest dynamic test finder
# Usage:
#     pytest
#     pytest -v                   # List all tests found
#     pytest -k day01             # Run all tests from day01
#     pytest -k "day01 and part1" # Run tests for first part of day01
#     pytest -k main              # Only run actual puzzles, not test inputs

import aoc2023

from pathlib import Path
import re


def pytest_generate_tests(metafunc):
    if metafunc.function == test:
        top_dir = Path(__file__).resolve().parent
        day_regex = re.compile(r"day(\d{2})")
        sample_regex = re.compile(r"sample\d+")

        # Dictionary from test_identifier to tuple of test arguments.
        tests: dict[str, tuple[int, Path, bool, int | str]] = {}

        for day_dir in sorted(top_dir.iterdir()):
            if day_match := day_regex.fullmatch(day_dir.name):
                day = int(day_match.group(1))
                data_dir = day_dir / "data"

                test_inputs = sorted([p for p in data_dir.iterdir() if sample_regex.fullmatch(p.name)]) + \
                    [data_dir / "input"]
                for test_input in test_inputs:
                    for part in [1, 2]:
                        answer_file = test_input.parent / f"{test_input.name}.answer{part}"
                        if answer_file.exists():
                            input_name = "main" if test_input.name == "input" else test_input.name
                            with open(answer_file) as f:
                                answer = f.read().strip()
                                if answer.isdigit():
                                    answer = int(answer)
                            tests[f"day{day:02} part{part}: {input_name}"] = (day, test_input, part == 1, answer)

        arguments = tests.items()
        metafunc.parametrize(["day", "input_path", "part1", "answer"], [arg[1] for arg in arguments],
            ids=[arg[0] for arg in arguments])


def test(day: int, input_path: Path, part1: bool, answer: int | str) -> None:
    assert aoc2023.run_puzzle(day, input_path, part1) == answer
