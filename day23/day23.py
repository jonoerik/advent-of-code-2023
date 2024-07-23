#!/usr/bin/env python3

import collections
from enum import IntEnum
from pathlib import Path


class Tile(IntEnum):
    PATH = 0
    FOREST = 1
    SLOPE_UP = 2  # Not observed in inputs, but left here for completeness.
    SLOPE_RIGHT = 3
    SLOPE_DOWN = 4
    SLOPE_LEFT = 5  # Not observed in inputs, but left here for completeness.


InputType = list[list[Tile]]
ResultType = int


def load(input_path: Path) -> InputType:
    with open(input_path) as f:
        return [[{".": Tile.PATH,
                  "#": Tile.FOREST,
                  "^": Tile.SLOPE_UP,
                  ">": Tile.SLOPE_RIGHT,
                  "v": Tile.SLOPE_DOWN,
                  "<": Tile.SLOPE_LEFT
                  }[c] for c in line.strip()] for line in f.readlines()]


def find_entry_egress(input_data: InputType) -> tuple[tuple[int, int], tuple[int, int]]:
    """Find the entry and exit (called egress, to avoid clashing with the Python keyword) points of the map."""
    # Check that the map has only one entry and one egress.
    assert all([r[0] == Tile.FOREST for r in input_data])
    assert all([r[-1] == Tile.FOREST for r in input_data])
    assert all([t in [Tile.PATH, Tile.FOREST] for t in input_data[0]]) and input_data[0].count(Tile.PATH) == 1
    assert all([t in [Tile.PATH, Tile.FOREST] for t in input_data[-1]]) and input_data[-1].count(Tile.PATH) == 1

    entry = (0, input_data[0].index(Tile.PATH))
    egress = (len(input_data) - 1, input_data[-1].index(Tile.PATH))

    return entry, egress


def build_graph(input_data: InputType) -> dict[tuple[int, int], list[tuple[tuple[int, int], int]]]:
    """Build the directed acyclic graph representing the map.
    Returns a dictionary of graph edges, as {start_coordinates: [(end_coordinates, path_length)]}.
    Path length includes end point, but not start point."""

    entry = (0, input_data[0].index(Tile.PATH))
    egress = (len(input_data) - 1, input_data[-1].index(Tile.PATH))

    def downhill_pos(p: tuple[int, int]) -> tuple[int, int]:
        """For a tile at position p which is a slope, return the position of the downhill tile."""
        return {Tile.SLOPE_UP: (p[0] - 1, p[1]),
                Tile.SLOPE_RIGHT: (p[0], p[1] + 1),
                Tile.SLOPE_DOWN: (p[0] + 1, p[1]),
                Tile.SLOPE_LEFT: (p[0], p[1] - 1)
                }[input_data[p[0]][p[1]]]

    def trace_path(start: tuple[int, int]) -> tuple[tuple[int, int], int]:
        """Starting at coordinates start (either a slope, or the entry tile), trace the path to the next slope or to the
        egress. Returns the final tile in the path, and the length of the path (including start, and final slope /
        egress)."""
        prev_pos = start
        current_pos = (start[0] + 1, start[1]) if start == entry else \
            {Tile.SLOPE_UP: (start[0] - 1, start[1]),
             Tile.SLOPE_RIGHT: (start[0], start[1] + 1),
             Tile.SLOPE_DOWN: (start[0] + 1, start[1]),
             Tile.SLOPE_LEFT: (start[0], start[1] - 1)
             }[input_data[start[0]][start[1]]]

        path_length = 2

        while current_pos != egress and input_data[current_pos[0]][current_pos[1]] == Tile.PATH:
            next_pos = None
            for next_r, next_c in [(current_pos[0] - 1, current_pos[1]), (current_pos[0] + 1, current_pos[1]),
                                   (current_pos[0], current_pos[1] - 1), (current_pos[0], current_pos[1] + 1)]:
                if (next_r, next_c) == prev_pos:
                    continue
                if input_data[next_r][next_c] != Tile.FOREST:
                    # If next_pos not None, current_pos has an unexpected branching path.
                    # We expect all branches to be surrounded by slope tiles.
                    assert next_pos is None
                    next_pos = (next_r, next_c)
            # If next_pos is None, we've hit an unexpected dead-end.
            assert next_pos is not None
            path_length += 1
            prev_pos = current_pos
            current_pos = next_pos

        if current_pos != egress:
            # Check that we haven't ended at an impassable uphill slope.
            assert downhill_pos(current_pos) != prev_pos

        return current_pos, path_length

    first_node, start_length = trace_path(entry)
    result = collections.defaultdict(list, {entry: [(downhill_pos(first_node), start_length)]})
    to_process = {downhill_pos(first_node)}
    processed = set()

    while to_process:
        node = to_process.pop()
        if node in processed:
            continue

        for segment_start in [(node[0] - 1, node[1]), (node[0] + 1, node[1]),
                              (node[0], node[1] - 1), (node[0], node[1] + 1)]:
            if input_data[segment_start[0]][segment_start[1]] != Tile.FOREST and \
                    downhill_pos(segment_start) != node:  # Only process outgoing paths.
                # Detect adjacent nodes (only a single slope between them).
                pos_after_start = downhill_pos(segment_start)
                if pos_after_start != egress and \
                        Tile.PATH not in [input_data[pos_after_start[0] + dr][pos_after_start[1] + dc]
                                          for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]]:
                    result[node].append((pos_after_start, 2))
                    to_process.add(pos_after_start)

                else:
                    segment_end, segment_length = trace_path(segment_start)

                    if segment_end == egress:
                        result[node].append((segment_end, segment_length))

                    else:
                        end_node = downhill_pos(segment_end)

                        # Assume the input has no loops.
                        assert end_node != node

                        result[node].append((downhill_pos(segment_end), segment_length + 1))
                        to_process.add(end_node)

        processed.add(node)

    # Check that the graph is acyclic, using a depth-first search.
    # If the graph contains cycles, the problem of finding the longest simple (no repeated nodes)
    # path is NP-hard. For a DAG, the longest path can be found in linear time.
    def check_cycles(n: tuple[int, int], visited: list[tuple[int, int]]):
        for (next_node, _) in result[n]:
            assert next_node not in visited
            check_cycles(next_node, visited + [n])

    check_cycles(entry, [])

    # Ensure end node was reached.
    assert egress in result.keys()

    return dict(result)


def part1(input_data: InputType) -> ResultType:
    entry, egress = find_entry_egress(input_data)
    graph = build_graph(input_data)

    # Negate all edge weights in graph.
    graph = {start: [(end, -cost) for end, cost in v] for start, v in graph.items()}

    def topological_sort() -> list[tuple[int, int]]:
        """Return a topological ordering of the nodes of graph, using depth-first search."""
        result = []
        visited = set()

        def visit(n: tuple[int, int]):
            if n in visited:
                return
            for next_n, _ in graph[n]:
                visit(next_n)
            visited.add(n)
            result.insert(0, n)

        visit(entry)
        return result

    def shortest_paths() -> dict[tuple[int, int], int]:
        """Return a dictionary of nodes, to the length of the shortest path to that node."""
        graph_incoming_edges: dict[tuple[int, int], list[tuple[int, int]]] = collections.defaultdict(list)
        for start, ends in graph.items():
            for end, _ in ends:
                graph_incoming_edges[end].append(start)

        result = {}
        for n in topological_sort():
            result[n] = min([0] + [min([result[from_node] + edge_cost for to_node, edge_cost in graph[from_node]
                                        if to_node == n])
                                   for from_node in graph_incoming_edges[n]])

        return result

    return -shortest_paths()[egress]


def part2(input_data: InputType) -> ResultType:
    pass  # TODO
