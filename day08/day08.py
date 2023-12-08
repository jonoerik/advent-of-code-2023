#!/usr/bin/env python3

from pathlib import Path
import re

InputType = tuple[str, dict[str, tuple[str, str]]]
ResultType = int


def load(input_path: Path) -> InputType:
    with open(input_path) as f:
        instructions = f.readline().strip()
        f.readline()  # Discard blank line.
        network_line_regex = re.compile(r"(\w+) = \((\w+), (\w+)\)")
        network = {match.group(1): (match.group(2), match.group(3))
                   for match in map(lambda line: network_line_regex.fullmatch(line.strip()), f.readlines())}
        return instructions, network


def part1(input_data: InputType) -> ResultType:
    current = "AAA"
    steps = 0
    while current != "ZZZ":
        current = input_data[1][current][0 if input_data[0][steps % len(input_data[0])] == "L" else 1]
        steps += 1
    return steps


def part2(input_data: InputType) -> ResultType:
    pass  #TODO
