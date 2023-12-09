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
    def prev_num(l: list[int]) -> int:
        sequence_deltas: list[list[int]] = [l]
        while not all([x == 0 for x in sequence_deltas[-1]]):
            sequence_deltas.append([b - a for a, b in itertools.pairwise(sequence_deltas[-1])])
        # Result for this one takes the left side of sequence_deltas, and alternates between adding and subtracting
        # values.
        return sum([x if i % 2 == 0 else -x for i, x in enumerate([sd[0] for sd in sequence_deltas])])

    return sum(map(prev_num, input_data))
