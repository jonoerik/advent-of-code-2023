#!/usr/bin/env python3

from enum import IntEnum
import heapq
from pathlib import Path
import typing

InputType = list[list[int]]
ResultType = int


def load(input_path: Path) -> InputType:
    with open(input_path) as f:
        return [[int(c) for c in line.strip()] for line in f.readlines()]


class Direction(IntEnum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3


class PathNode(typing.NamedTuple):
    """A node in the pathfinding graph. Encodes current position, and the length and direction of the last
    straight-line move. This means that reaching the same position from a different direction is encoded differently,
    to allow for the restriction on the length of straight-line moves."""
    row: int
    col: int
    last_move_direction: Direction | None
    last_move_length: int


def min_heat_loss(input_data: InputType, start_pos: tuple[int, int], end_pos: tuple[int, int],
                  min_straight_length: int, max_straight_length: int) -> int:
    """Use A* Algorithm."""

    def h(row: int, col: int) -> int:
        """A* heuristic for cost of path from (row, col) to end_pos.
        This must always be less than or equal to the actual cost of reaching the end, for A* to follow an optimal
        path (i.e. h must be admissible)."""
        # Assume every tile between here and the end is 1.
        return len(input_data) - row + len(input_data[0]) - col

    # Heap of (distance to node + expected distance to end, distance to node, node) to visit next.
    next_nodes: list[tuple[int, int, PathNode]] = []
    # Dict of nodes already visited, to the cost to reach that node.
    visited: dict[PathNode, int] = {}
    heapq.heappush(next_nodes, (h(*start_pos), 0, PathNode(start_pos[0], start_pos[1], None, 0)))

    while next_nodes:
        expected, dist, node = heapq.heappop(next_nodes)
        # Allow nodes to be revisited if they've been only been seen before with a higher cost.
        # This allows us to write a heuristic that's only admissible, but doesn't have to be consistent.
        if node in visited and visited[node] <= dist:
            continue
        visited[node] = dist

        if (node.row, node.col) == end_pos and min_straight_length <= node.last_move_length:
            return dist

        for d in Direction:
            if d == {Direction.UP: Direction.DOWN, Direction.RIGHT: Direction.LEFT,
                     Direction.DOWN: Direction.UP, Direction.LEFT: Direction.RIGHT,
                     None: None}[node.last_move_direction]:
                # No u-turns.
                continue
            if node.last_move_direction is not None and d != node.last_move_direction and \
                    node.last_move_length < min_straight_length:
                # No turning before min_straight_length.
                continue
            new_move_length = node.last_move_length + 1 if node.last_move_direction == d else 1
            if new_move_length > max_straight_length:
                # Must turn within max_straight_length.
                continue
            new_row = node.row + {Direction.UP: -1, Direction.RIGHT: 0, Direction.DOWN: 1, Direction.LEFT: 0}[d]
            new_col = node.col + {Direction.UP: 0, Direction.RIGHT: 1, Direction.DOWN: 0, Direction.LEFT: -1}[d]
            if not (0 <= new_row < len(input_data) and 0 <= new_col < len(input_data[0])):
                # Can't go outside bounds of the city.
                continue

            new_node = PathNode(new_row, new_col, d, new_move_length)
            new_dist = dist + input_data[new_row][new_col]
            heapq.heappush(next_nodes, (new_dist + h(new_row, new_col), new_dist, new_node))

    # Should have found a path to the end before running out of nodes.
    assert False


def part1(input_data: InputType) -> ResultType:
    return min_heat_loss(input_data, (0, 0), (len(input_data)-1, len(input_data[0])-1), 1, 3)


def part2(input_data: InputType) -> ResultType:
    return min_heat_loss(input_data, (0, 0), (len(input_data)-1, len(input_data[0])-1), 4, 10)
