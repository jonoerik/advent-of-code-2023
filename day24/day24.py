#!/usr/bin/env python3

import itertools
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


def part1(input_data: InputType,
          test_area_min: int = 200_000_000_000_000,
          test_area_max: int = 400_000_000_000_000) -> ResultType:

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

    return len([None for x, y in
                [t for t in
                 [intersection_2d(a, b) for a, b in itertools.combinations(input_data, 2)]
                 if t is not None]
                if test_area_min <= x <= test_area_max and test_area_min <= y <= test_area_max])


def part2(input_data: InputType) -> ResultType:
    pass  # TODO
