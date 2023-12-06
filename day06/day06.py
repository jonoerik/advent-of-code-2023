#!/usr/bin/env python3

import math
from pathlib import Path

# List of races (time, distance)
InputType = list[tuple[int, int]]
ResultType = int


def load(input_path: Path) -> InputType:
    with open(input_path) as f:
        return list(zip([int(x) for x in f.readline().split()[1:]], [int(x) for x in f.readline().split()[1:]]))


def part1(input_data: InputType) -> ResultType:
    def race_wins(time: int, distance: int) -> int:
        result = 0
        for t in range(1, time):
            # No need to check t == 0 or t == time, as these never travel any distance.
            if t * (time - t) > distance:
                result += 1
        return result

    return math.prod([race_wins(t, d) for t, d in input_data])


def part2(input_data: InputType) -> ResultType:
    pass  #TODO
