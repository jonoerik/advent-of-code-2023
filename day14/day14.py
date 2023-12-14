#!/usr/bin/env python3

from pathlib import Path

InputType = list[str]
ResultType = int


def load(input_path: Path) -> InputType:
    with open(input_path) as f:
        return [line.strip() for line in f.readlines()]


def part1(input_data: InputType) -> ResultType:
    # Transpose input_data, as working row-by-row will be easier.
    input_data = ["".join(col) for col in zip(*input_data)]
    # Load produced by a single rounded rock at the north-most edge.
    max_load = len(input_data[0])
    total_load = 0
    # Don't actually move the rounded rocks, just calculate what their load would be if moved.
    for row in input_data:
        next_load = max_load
        for i, c in enumerate(row):
            if c == "O":
                total_load += next_load
                next_load -= 1
            elif c == "#":
                next_load = max_load - i - 1
    return total_load


def part2(input_data: InputType) -> ResultType:
    pass  #TODO
