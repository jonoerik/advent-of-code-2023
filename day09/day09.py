#!/usr/bin/env python3

import itertools
from pathlib import Path

InputType = list[list[int]]
ResultType = int


def load(input_path: Path) -> InputType:
    with open(input_path) as f:
        return [[int(x) for x in line.strip().split(" ")]for line in f.readlines()]


def part1(input_data: InputType) -> ResultType:
    def next_num(l: list[int]) -> int:
        sequence_deltas: list[list[int]] = [l]
        while not all([x == 0 for x in sequence_deltas[-1]]):
            sequence_deltas.append([b - a for a, b in itertools.pairwise(sequence_deltas[-1])])
        return sum([sd[-1] for sd in sequence_deltas])

    return sum(map(next_num, input_data))


def part2(input_data: InputType) -> ResultType:
    pass  #TODO
