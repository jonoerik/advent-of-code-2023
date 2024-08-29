#!/usr/bin/env python3

from pathlib import Path
import re


InputType = dict[str, set[str]]
ResultType = int


def load(input_path: Path) -> InputType:
    line_regex = re.compile(r"^(\w{3}): (\w{3}(?: \w{3})*)$")
    with open(input_path) as f:
        return {match.group(1): set(match.group(2).split())
                for match in [line_regex.fullmatch(line.strip()) for line in f.readlines()]}


def part1(input_data: InputType) -> ResultType:
    print(input_data)
    pass  # TODO


def part2(input_data: InputType) -> ResultType:
    pass  # TODO
