#!/usr/bin/env python3

from pathlib import Path

InputType = list[str]
ResultType = int


def load(input_path: Path) -> InputType:
    with open(input_path) as f:
        return [line.strip() for line in f.readlines()]


def find_start(input_data: InputType) -> tuple[int, int]:
    """Returns row, col of starting point."""
    for row, line in enumerate(input_data):
        if "S" in line:
            return row, line.index("S")


def start_pipe(input_data: InputType, start_row: int, start_col: int) -> str:
    """Returns the character representing the pipe on the start location."""
    left = False if start_col == 0 else (input_data[start_row][start_col - 1] in "-LF")
    right = False if start_col == len(input_data[0]) - 1 else (input_data[start_row][start_col + 1] in "-J7")
    up = False if start_row == 0 else (input_data[start_row - 1][start_col] in "|7F")
    down = False if start_row == len(input_data) - 1 else (input_data[start_row + 1][start_col] in "|LJ")
    return {
        (False, False, True, True): "|",
        (True, True, False, False): "-",
        (False, True, True, False): "L",
        (True, False, True, False): "J",
        (True, False, False, True): "7",
        (False, True, False, True): "F",
    }[(left, right, up, down)]


def adjacent_pipe_segment(input_data: InputType, row: int, col: int) -> tuple[tuple[int, int], tuple[int, int]]:
    """Returns the (row, col) of the two pipe segments adjacent to this one."""
    return {
        "|": ((row - 1, col), (row + 1, col)),
        "-": ((row, col - 1), (row, col + 1)),
        "L": ((row - 1, col), (row, col + 1)),
        "J": ((row - 1, col), (row, col - 1)),
        "7": ((row + 1, col), (row, col - 1)),
        "F": ((row + 1, col), (row, col + 1)),
    }[input_data[row][col]]


def part1(input_data: InputType) -> ResultType:
    start = find_start(input_data)
    input_data[start[0]] = \
        input_data[start[0]][:start[1]] + start_pipe(input_data, *start) + input_data[start[0]][start[1] + 1:]

    steps = 1
    prev_pos = start
    pos = adjacent_pipe_segment(input_data, *start)[0]
    while pos != start:
        adj = adjacent_pipe_segment(input_data, *pos)
        if adj[0] == prev_pos:
            prev_pos = pos
            pos = adj[1]
        else:
            prev_pos = pos
            pos = adj[0]
        steps += 1
    assert steps % 2 == 0
    return steps // 2


def part2(input_data: InputType) -> ResultType:
    start = find_start(input_data)
    input_data[start[0]] = \
        input_data[start[0]][:start[1]] + start_pipe(input_data, *start) + input_data[start[0]][start[1] + 1:]

    # Remove all non-loop pipe segments, replacing them with open ground.
    prev_pos = start
    pos = adjacent_pipe_segment(input_data, *start)[0]
    loop = [pos]
    while pos != start:
        adj = adjacent_pipe_segment(input_data, *pos)
        if adj[0] == prev_pos:
            prev_pos = pos
            pos = adj[1]
        else:
            prev_pos = pos
            pos = adj[0]
        loop.append(pos)
    input_data = ["".join([char if (row, col) in loop else "." for col, char in enumerate(line)]) for row, line in enumerate(input_data)]

    # Expand the original m x n map into a 3m x 3n map with ascii-art representations of each tile.
    #
    #      ...         .#.
    # 7 -> ##.    | -> .#.   etc.
    #      .#.         .#.
    #
    # True represents a pipe boundary, and False is open ground.
    expanded_map = [[{
        ".": [[False, False, False], [False, False, False], [False, False, False]],
        "|": [[False, True, False], [False, True, False], [False, True, False]],
        "-": [[False, False, False], [True, True, True], [False, False, False]],
        "L": [[False, True, False], [False, True, True], [False, False, False]],
        "J": [[False, True, False], [True, True, False], [False, False, False]],
        "7": [[False, False, False], [True, True, False], [False, True, False]],
        "F": [[False, False, False], [False, True, True], [False, True, False]],
                     }[input_data[row // 3][col // 3]][row % 3][col % 3]
        for col in range(3 * len(input_data[0]))] for row in range(3 * len(input_data))]

    # Flood fill from upper-left corner (which can't be inside the loop).
    # Entire outer perimeter of the expanded map must initially be False, as the loop can't extend outside the outer
    # bounds of the original map.
    next_cells: set[tuple[int, int]] = {(0, 0)}
    while len(next_cells) > 0:
        current = next_cells.pop()
        expanded_map[current[0]][current[1]] = True
        for row, col in [(current[0] - 1, current[1]),
                         (current[0] + 1, current[1]),
                         (current[0], current[1] - 1),
                         (current[0], current[1] + 1)]:
            if 0 <= row < len(expanded_map) and 0 <= col < len(expanded_map[0]) and not expanded_map[row][col]:
                next_cells.add((row, col))

    # For each open cell on the original map, check if the centre cell for that tile in the expanded map
    # has been filled in by the flood fill. Unfilled cells are inside the loop.
    return sum([sum([1 if not expanded_map[row * 3 + 1][col * 3 + 1] else 0
                     for col, cell in enumerate(line) if cell == "."])
                for row, line in enumerate(input_data)])
