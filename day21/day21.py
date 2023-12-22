#!/usr/bin/env python3

from pathlib import Path

InputType = list[str]
ResultType = int


def load(input_path: Path) -> InputType:
    with open(input_path) as f:
        return [line.strip() for line in f.readlines()]


def part1(input_data: InputType, steps: int = 64) -> ResultType:
    input_data = [row.replace("S", "O") for row in input_data]

    def neighbourhood(r: int, c: int) -> int:
        return [input_data[r + dr][c + dc] for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]
                if 0 <= r + dr < len(input_data) and 0 <= c + dc < len(input_data[0])].count("O")

    for _ in range(steps):
        new_garden = ["".join([cell if cell == "#" else ("O" if neighbourhood(row_index, col_index) > 0 else ".")
                               for col_index, cell in enumerate(row)]) for row_index, row in enumerate(input_data)]
        input_data = new_garden

    return sum([row.count("O") for row in input_data])


def part2(input_data: InputType) -> ResultType:
    pass  #TODO
