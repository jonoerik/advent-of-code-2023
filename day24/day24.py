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


def check_solvable(m_in: list[list[int]]) -> bool:
    """Perform Gaussian Elimination on the linear system of equations given by augmented matrix m_in.
    The system is only processed to row echelon form, not reduced row echelon form, and this function may return early
    if the system has no solutions.
    Return True if the system has solutions, False otherwise.
    The reduction is done using floating point calculations, so it's susceptible to floating point errors.
    Numbers are treated as equal to 0 if they are within +/- zero_error of 0.
    If this returns true, this only indicates that the linear system m_in may have a solution.
    A more precise solve should be done to confirm this."""
    m = [[float(cell) for cell in row] for row in m_in]
    zero_error = 1e-6

    def is_zero(n: float):
        return -zero_error <= n <= zero_error

    def swap_rows(r1: int, r2: int) -> None:
        a = m[r1]
        b = m[r2]
        m[r2] = a
        m[r1] = b

    def scale_add_row(r_dest: int, r_src: int, s: float) -> None:
        assert not is_zero(s)
        assert r_dest != r_src
        m[r_dest] = [a + s * b for a, b in zip(m[r_dest], m[r_src])]

    current_col = 0
    # Dictionary from column index, to row index that contains the leading nonzero value for that column.
    leading_rows: dict[int, int] = {}
    current_row = 0
    while current_row < len(m):
        # Don't try to reduce away the last column of the augmented matrix.
        if current_col < len(m[0]) - 1:
            if is_zero(m[current_row][current_col]):
                for search_row in range(current_row + 1, len(m)):
                    if not is_zero(m[search_row][current_col]):
                        swap_rows(current_row, search_row)
                        break
                else:
                    # No remaining rows have a nonzero value in current_col; so skip that column.
                    current_col += 1
                    continue

            for c in leading_rows.keys():
                if not is_zero(m[current_row][c]):
                    scale_add_row(current_row, leading_rows[c], -m[current_row][c] / m[leading_rows[c]][c])

            leading_rows[current_col] = current_row
            for lower_row in range(current_row + 1, len(m)):
                if not is_zero(m[lower_row][current_col]):
                    scale_add_row(lower_row, current_row, -m[lower_row][current_col] / m[current_row][current_col])
            current_col += 1
        else:
            if not is_zero(m[current_row][-1]):
                # Shouldn't be able to get this far with non-zero values in any non-last column in this row.
                assert all(is_zero(c) for c in m[current_row][0:-1])
                # This row states that 0 == nonzero value, therefore the system has no solution.
                return False

        current_row += 1

    return True


# Global value used to pass input_data in a multiprocessing-safe way to each subprocess.
input_data_global: InputType


def try_solve(v: tuple[int, int, int]) -> tuple[int, int, int] | None:
    """Try to solve for velocity = v. If successful, return start position of the rock, otherwise return None."""
    linear_system = []

    def add_linear_equations(n):
        h = input_data_global[n]
        linear_system.append([1, 0, 0] + ([0] * n) +
                             [v[0] - h.vel[0]] + ([0] * (len(input_data_global) - n - 1)) + [h.pos[0]])
        linear_system.append([0, 1, 0] + ([0] * n) +
                             [v[1] - h.vel[1]] + ([0] * (len(input_data_global) - n - 1)) + [h.pos[1]])
        linear_system.append([0, 0, 1] + ([0] * n) +
                             [v[2] - h.vel[2]] + ([0] * (len(input_data_global) - n - 1)) + [h.pos[2]])

    # Do an initial check with only 2 lines, so that we can quickly eliminate most candidate velocities.
    add_linear_equations(0)
    add_linear_equations(1)

    if not check_solvable(linear_system):
        return None

    # Add the remaining line equations, for the final accurate check.
    for i in range(2, len(input_data_global)):
        add_linear_equations(i)

    unknowns = [sympy.Symbol(f"rock_{d}") for d in ["x", "y", "z"]] + \
               [sympy.Symbol(f"t_{ti}") for ti in range(len(input_data_global))]
    solution = sympy.solve_linear_system(sympy.Matrix(linear_system), *unknowns)
    if not solution:
        return None

    return solution[unknowns[0]], solution[unknowns[1]], solution[unknowns[2]]


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

    def init_fn(input_data_param) -> None:
        global input_data_global
        input_data_global = input_data_param

    with multiprocessing.Pool(initializer=init_fn, initargs=(input_data,)) as pool:
        # At the default chunksize, subprocesses weren't fully utilising CPU cores.
        # If needed, chunksize can be increased further to achieve 100% CPU utilisation.
        for position in pool.imap(try_solve, next_trial_v(), chunksize=1000):
            if position is not None:
                return sum(position)
