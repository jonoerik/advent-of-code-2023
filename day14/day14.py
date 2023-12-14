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
    def roll_line_right(line: str) -> str:
        areas_between_squares = line.split("#")
        return "#".join([("." * (len(area) - rounded_boulders)) + ("O" * rounded_boulders)
                         for area, rounded_boulders in [(area, area.count("O")) for area in areas_between_squares]])

    def spin_cycle() -> None:
        nonlocal input_data
        for cycle in range(4):
            # Rotate clockwise, and roll each line to the right.
            input_data = [roll_line_right("".join(reversed(col))) for col in zip(*input_data)]

    # Memo of input_data state, to the value of i when that state was first seen.
    memo: dict[tuple[str], int] = {}
    total_spin_cycles = 1_000_000_000
    for i in range(total_spin_cycles):
        if tuple(input_data) not in memo.keys():
            memo[tuple(input_data)] = i
        else:
            # We've found a loop in the input_data states.
            loop_length = i - memo[tuple(input_data)]
            # We can skip a multiple of the loop length in cycles, and only do the few remaining final cycles.
            cycles_remaining = (total_spin_cycles - i) % loop_length
            for j in range(cycles_remaining):
                spin_cycle()
            break

        spin_cycle()

    return sum([line.count("O") * (len(input_data) - i) for i, line in enumerate(input_data)])
