#!/usr/bin/env python3

from pathlib import Path
import re

# List of input file lines.
InputType = list[str]
ResultType = int


def load(input_path: Path) -> InputType:
    with open(input_path) as f:
        return [line.strip() for line in f.readlines()]


partnum_regex = re.compile(r"(?<![0-9])(\d+)(?![0-9])")


def part1(input_data: InputType) -> ResultType:
    height = len(input_data)
    width = len(input_data[0])
    total = 0

    contains_symbol_regex = re.compile(r"[^0-9.]")

    def symbol_nearby(row_start: int, row_end: int, col_start: int, col_end: int) -> bool:
        """
        *_start are inclusive, *_end are exclusive
        """
        for row in range(row_start, row_end):
            if contains_symbol_regex.search(input_data[row][col_start:col_end]):
                return True
        return False

    for i, line in enumerate(input_data):
        for match in partnum_regex.finditer(line):
            if symbol_nearby(max(0, i-1), min(height, i+2), max(0, match.start()-1), min(width, match.end()+1)):
                total += int(match.group(0))

    return total


def part2(input_data: InputType) -> ResultType:
    height = len(input_data)
    width = len(input_data[0])
    total = 0

    # List of neighbourhoods, paired with their corresponding partnum integers.
    # Neighbourhood is the area around a partnum, as (row_start, row_end, col_start, col_end).
    # *_start is inclusive, *_end is exclusive.
    partnum_neighbourhoods: list[tuple[tuple[int, int, int, int], int]] = []
    for i, line in enumerate(input_data):
        for match in partnum_regex.finditer(line):
            partnum_neighbourhoods.append(((max(0, i-1), min(height, i+2),
                                            max(0, match.start()-1), min(width, match.end()+1)),
                                           int(match.group(0))))

    for i, line in enumerate(input_data):
        for j in [pos for pos, char in enumerate(line) if char == "*"]:
            neighbours = list(filter(lambda x: (x[0][0] <= i < x[0][1] and x[0][2] <= j < x[0][3]),
                                     partnum_neighbourhoods))
            if len(neighbours) == 2:
                total += neighbours[0][1] * neighbours[1][1]

    return total
