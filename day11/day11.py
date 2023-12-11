#!/usr/bin/env python3

import itertools
from pathlib import Path

# True for each galaxy, false otherwise.
InputType = list[list[bool]]
ResultType = int


def load(input_path: Path) -> InputType:
    with open(input_path) as f:
        return [[char == "#" for char in line.strip()] for line in f.readlines()]


def part1(input_data: InputType) -> ResultType:
    # Expand space.
    empty_rows = reversed([row for row, line in enumerate(input_data) if not any(line)])
    empty_cols = reversed([col for col in range(len(input_data[0])) if not any([line[col] for line in input_data])])
    # Index lists are reversed, so early inserts don't alter the position of later inserts.
    for empty_row in empty_rows:
        input_data.insert(empty_row, [False for _ in range(len(input_data[0]))])
    for empty_col in empty_cols:
        for row in input_data:
            row.insert(empty_col, False)

    # Find galaxies, as a list of (row, col).
    galaxies: list[tuple[int, int]] = \
        [(row, col) for row, line in enumerate(input_data) for col, cell in enumerate(line) if cell]

    return sum([abs(a[0] - b[0]) + abs(a[1] - b[1]) for a, b in itertools.combinations(galaxies, 2)])


def part2(input_data: InputType, expansion_factor: int = 1_000_000) -> ResultType:
    empty_rows = [row for row, line in enumerate(input_data) if not any(line)]
    empty_cols = [col for col in range(len(input_data[0])) if not any([line[col] for line in input_data])]
    galaxies: list[tuple[int, int]] = \
        [(row, col) for row, line in enumerate(input_data) for col, cell in enumerate(line) if cell]

    total_distance = 0
    for a, b in itertools.combinations(galaxies, 2):
        row_range = range(min(a[0], b[0]) + 1, max(a[0], b[0]))
        col_range = range(min(a[1], b[1]) + 1, max(a[1], b[1]))
        total_distance += abs(a[0] - b[0]) + (expansion_factor - 1) * len([x for x in empty_rows if x in row_range]) + \
            abs(a[1] - b[1]) + (expansion_factor - 1) * len([x for x in empty_cols if x in col_range])
    return total_distance
