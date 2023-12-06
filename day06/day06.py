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
    time = int("".join([str(x) for x, _ in input_data]))
    distance = int("".join([str(y) for _, y in input_data]))
    # Graph of distance travelled (y), against time button held (x), is a downwards-opening parabola, with intercepts at
    # x = 0 and x = time. We need to find the points where this parabola intersects y = distance, which we can do with
    # the quadratic formula. We then take the ceiling, which gives the first button-time which beats the record.
    # From the symmetry of the graph, we know that the other intersection will be at time - min_time_to_win, and we
    # can calculate the number of time options between the two.
    min_time_to_win = math.ceil((time - math.sqrt(time ** 2 - 4 * distance)) / 2)
    return time - 2 * min_time_to_win + 1
