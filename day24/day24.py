#!/usr/bin/env python3

import collections.abc
import itertools
import multiprocessing
from pathlib import Path
import re
import sympy


class Hailstone:
    def __init__(self, pos: tuple[int, int, int], vel: tuple[int, int, int]):
        self.pos = pos
        self.vel = vel


InputType = list[Hailstone]
ResultType = int


def load(input_path: Path) -> InputType:
    line_regex = re.compile(r"^(-?\d+), +(-?\d+), +(-?\d+) +@ +(-?\d+), +(-?\d+), +(-?\d+)$")
    with open(input_path) as f:
        return [Hailstone((int(match.group(1)), int(match.group(2)), int(match.group(3))),
                          (int(match.group(4)), int(match.group(5)), int(match.group(6))))
                for match in [line_regex.fullmatch(line.strip()) for line in f.readlines()]]


def intersection_2d(h1: Hailstone, h2: Hailstone) -> tuple[sympy.core.Number, sympy.core.Number] | None:
    # Find intersection by solving set of linear equations:
    # h1.x + h1.vx * t1 = h2.x + h2.vx * t2
    # h1.y + h1.vy * t1 = h2.y + h2.vy * t2
    # ===
    # h1.vx * t1 - h2.vx * t2 = h2.x - h1.x
    # h1.vy * t1 - h2.vy * t2 = h2.y - h1.y
    # Solve m*t = p
    m = sympy.Matrix([[h1.vel[0], -h2.vel[0]], [h1.vel[1], -h2.vel[1]]])
    p = sympy.Matrix(2, 1, [h2.pos[0] - h1.pos[0], h2.pos[1] - h1.pos[1]])
    if m.det() == 0:
        # Hailstone paths don't intersect.
        return None
    t = m.inv() * p
    if t[0] < 0 or t[1] < 0:
        # Intersection occurred in the past.
        return None
    return h1.pos[0] + h1.vel[0] * t[0, 0], h1.pos[1] + h1.vel[1] * t[0, 0]


def check_intersection(h1: Hailstone, h2: Hailstone, test_area_min: int, test_area_max: int):
    intersection = intersection_2d(h1, h2)
    return intersection is not None and \
        test_area_min <= intersection[0] <= test_area_max and \
        test_area_min <= intersection[1] <= test_area_max


def part1(input_data: InputType,
          test_area_min: int = 200_000_000_000_000,
          test_area_max: int = 400_000_000_000_000) -> ResultType:

    with multiprocessing.Pool() as pool:
        return pool.starmap(check_intersection,
                            [(h1, h2, test_area_min, test_area_max) for h1, h2 in itertools.combinations(input_data, 2)]
                            ).count(True)


def part2(input_data: InputType) -> ResultType:
    # Thanks to u/xiaowuc1 in reddit.com/r/adventofcode for the suggestion of brute forcing velocity vectors.
    # https://www.reddit.com/r/adventofcode/comments/18pptor/comment/keps780

    def next_trial_v() -> collections.abc.Iterator[tuple[int, int, int]]:
        """Yield all tuple[int, int, int], except (0, 0, 0), starting with those closest to (0, 0, 0) and then expanding
        out layer by layer."""
        for n in itertools.count(1):
            for z in [-n, n]:
                for y in range(-n, n+1):
                    for x in range(-n, n+1):
                        yield x, y, z
            for y in [-n, n]:
                for z in range(-n+1, n):
                    for x in range(-n, n+1):
                        yield x, y, z
            for x in [-n, n]:
                for z in range(-n+1, n):
                    for y in range(-n+1, n):
                        yield x, y, z

    unknowns = [sympy.Symbol(f"rock_{d}") for d in ["x", "y", "z"]] + \
               [sympy.Symbol(f"t_{ti}") for ti in range(len(input_data))]

    def try_solve(v: tuple[int, int, int]) -> tuple[int, int, int] | None:
        """Try to solve for velocity = v. If successful, return start position of the rock, otherwise return None."""
        linear_system = []
        for i, h in enumerate(input_data):
            linear_system.append([1, 0, 0] + ([0] * i) +
                                 [v[0] - h.vel[0]] + ([0] * (len(input_data) - i - 1)) + [h.pos[0]])
            linear_system.append([0, 1, 0] + ([0] * i) +
                                 [v[1] - h.vel[1]] + ([0] * (len(input_data) - i - 1)) + [h.pos[1]])
            linear_system.append([0, 0, 1] + ([0] * i) +
                                 [v[2] - h.vel[2]] + ([0] * (len(input_data) - i - 1)) + [h.pos[2]])

        solution = sympy.solve_linear_system(sympy.Matrix(linear_system), *unknowns)
        if solution:
            return solution[unknowns[0]], solution[unknowns[1]], solution[unknowns[2]]

    for velocity in next_trial_v():
        if position := try_solve(velocity):
            return sum(position)
