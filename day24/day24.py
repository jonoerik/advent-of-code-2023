#!/usr/bin/env python3

import itertools
import multiprocessing
from pathlib import Path
import re
import sympy
from sympy import Matrix

from .find_intersecting_line import *


class Hailstone:
    def __init__(self, pos: Matrix, vel: Matrix):
        self.pos = pos
        self.vel = vel


InputType = list[Hailstone]
ResultType = int


def load(input_path: Path) -> InputType:
    line_regex = re.compile(r"^(-?\d+), +(-?\d+), +(-?\d+) +@ +(-?\d+), +(-?\d+), +(-?\d+)$")
    with open(input_path) as f:
        return [Hailstone(Matrix([int(match.group(1)), int(match.group(2)), int(match.group(3))]),
                          Matrix([int(match.group(4)), int(match.group(5)), int(match.group(6))]))
                for match in [line_regex.fullmatch(line.strip()) for line in f.readlines()]]


def intersection_2d(h1: Hailstone, h2: Hailstone) -> Matrix | None:
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
    if t[0,0] < 0 or t[1,0] < 0:
        # Intersection occurred in the past.
        return None
    return Matrix([h1.pos[0,0] + h1.vel[0,0] * t[0,0], h1.pos[1,0] + h1.vel[1,0] * t[0,0]])


def check_intersection(h1: Hailstone, h2: Hailstone, test_area_min: int, test_area_max: int):
    intersection = intersection_2d(h1, h2)
    return intersection is not None and \
        test_area_min <= intersection[0,0] <= test_area_max and \
        test_area_min <= intersection[1,0] <= test_area_max


def part1(input_data: InputType,
          test_area_min: int = 200_000_000_000_000,
          test_area_max: int = 400_000_000_000_000) -> ResultType:

    with multiprocessing.Pool() as pool:
        return pool.starmap(check_intersection,
                            [(h1, h2, test_area_min, test_area_max) for h1, h2 in itertools.combinations(input_data, 2)]
                            ).count(True)


def part2(input_data: InputType) -> ResultType:
    def solve_for_l(l: Line) -> Matrix:
        """With rock trajectory l, solve for rock initial position."""

        def intersection_3d(l: Line, h: Hailstone) -> sympy.core.numbers.Number:
            """Find the time at which h's trajectory intersects with l. Line l is just a line in 3D space, with no time
            component."""
            linear_system = sympy.Matrix.hstack(
                l.p2[:3,:] - l.p1[:3,:],
                -h.vel,
                h.pos - l.p1[:3,:]
            )
            unknowns = sympy.symbols("t1 t2")
            ts = sympy.solve_linear_system(linear_system, *unknowns)
            assert ts is not None

            return ts[unknowns[1]]

        h1 = input_data[0]
        h2 = input_data[1]
        t1 = intersection_3d(l, h1)
        t2 = intersection_3d(l, h2)
        v = ((h2.pos + t2 * h2.vel) - (h1.pos + t1 * h1.vel)) / (t2 - t1)
        return h1.pos + (t1 * h1.vel) - (t1 * v)

    line = find_intersecting_line([Line(l.pos[0], l.pos[1], l.pos[2], l.vel[0], l.vel[1], l.vel[2])
                                   for l in input_data])
    assert line is not None
    return sum(solve_for_l(line))
