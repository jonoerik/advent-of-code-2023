#!/usr/bin/env python3

from enum import IntEnum
from pathlib import Path
import re


class Direction(IntEnum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3


InputType = list[tuple[Direction, int, tuple[int, int, int]]]
ResultType = int


def load(input_path: Path) -> InputType:
    line_regex = \
        re.compile(r"^(?P<dir>[URDL]) (?P<dist>\d+) \(#(?P<r>[0-9a-f]{2})(?P<g>[0-9a-f]{2})(?P<b>[0-9a-f]{2})\)$")
    with open(input_path) as f:
        return [({"U": Direction.UP,
                  "R": Direction.RIGHT,
                  "D": Direction.DOWN,
                  "L": Direction.LEFT}[match.group("dir")],
                 int(match.group("dist")),
                 (int(match.group("r"), 16), int(match.group("g"), 16), int(match.group("b"), 16)))
                for match in map(line_regex.fullmatch, [line.strip() for line in f.readlines()])]


def part1(input_data: InputType) -> ResultType:
    def dig_trench() -> list[list[bool]]:
        row = 0
        col = 0
        result = [[True]]
        for direction, dist, colour in input_data:
            match direction:
                case Direction.UP:
                    dist_to_edge = min(row, dist)
                    for i in range(dist_to_edge):
                        result[row - i - 1][col] = True
                    if dist_to_edge < dist:
                        result = [[c == col for c in range(len(result[0]))]
                                  for _ in range(dist - dist_to_edge)] + result
                    row = max(0, row - dist)
                case Direction.RIGHT:
                    dist_to_edge = min(len(result[0]) - 1 - col, dist)
                    for i in range(dist_to_edge):
                        result[row][col + i + 1] = True
                    if dist_to_edge < dist:
                        result = [r + [n == row for _ in range(dist - dist_to_edge)]
                                  for n, r in enumerate(result)]
                    col += dist
                case Direction.DOWN:
                    dist_to_edge = min(len(result) - 1 - row, dist)
                    for i in range(dist_to_edge):
                        result[row + i + 1][col] = True
                    if dist_to_edge < dist:
                        result = result + [[c == col for c in range(len(result[0]))]
                                           for _ in range(dist - dist_to_edge)]
                    row += dist
                case Direction.LEFT:
                    dist_to_edge = min(col, dist)
                    for i in range(dist_to_edge):
                        result[row][col - i - 1] = True
                    if dist_to_edge < dist:
                        result = [[n == row for _ in range(dist - dist_to_edge)] + r
                                  for n, r in enumerate(result)]
                    col = max(0, col - dist)
        return result
    trench = dig_trench()

    def dig_middle() -> list[list[bool]]:
        result = [[True for _ in range(len(trench[0]))] for _ in range(len(trench))]
        # Flood fill from outer edges.
        to_visit = {(0, i) for i in range(len(trench[0]))} | {(len(trench) - 1, i) for i in range(len(trench[0]))} | \
                   {(i, 0) for i in range(len(trench))} | {(i, len(trench[0]) - 1) for i in range(len(trench))}
        while to_visit:
            visiting = to_visit.pop()
            if 0 <= visiting[0] < len(trench) and 0 <= visiting[1] < len(trench[0]) and \
                    result[visiting[0]][visiting[1]] and not trench[visiting[0]][visiting[1]]:
                result[visiting[0]][visiting[1]] = False
                to_visit.update({(visiting[0] + dr, visiting[1] + dc) for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]})
        return result
    pit = dig_middle()

    return sum([1 if cell else 0 for row in pit for cell in row])


def part2(input_data: InputType) -> ResultType:
    pass  #TODO
