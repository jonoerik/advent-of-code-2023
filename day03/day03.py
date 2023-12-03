#!/usr/bin/env python3

from pathlib import Path
import re

# List of input file lines.
InputType = list[str]
ResultType = int


def load(input_path: Path) -> InputType:
    with open(input_path) as f:
        return [line.strip() for line in f.readlines()]


def part1(input_data: InputType) -> ResultType:
    height = len(input_data)
    width = len(input_data[0])
    total = 0

    partnum_regex = re.compile(r"(?<![0-9])(\d+)(?![0-9])")
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
    pass  #TODO
