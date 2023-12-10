#!/usr/bin/env python3

from pathlib import Path

InputType = list[str]
ResultType = int


def load(input_path: Path) -> InputType:
    with open(input_path) as f:
        return [line.strip() for line in f.readlines()]


def part1(input_data: InputType) -> ResultType:
    def find_start() -> tuple[int, int]:
        """Returns row, col of starting point."""
        for row, line in enumerate(input_data):
            if "S" in line:
                return row, line.index("S")

    def start_pipe(start_row: int, start_col: int) -> str:
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

    def adjacent_pipe_segment(row: int, col: int) -> tuple[tuple[int, int], tuple[int, int]]:
        """Returns the (row, col) of the two pipe segments adjacent to this one."""
        return {
            "|": ((row - 1, col), (row + 1, col)),
            "-": ((row, col - 1), (row, col + 1)),
            "L": ((row - 1, col), (row, col + 1)),
            "J": ((row - 1, col), (row, col - 1)),
            "7": ((row + 1, col), (row, col - 1)),
            "F": ((row + 1, col), (row, col + 1)),
        }[input_data[row][col]]

    start = find_start()
    input_data[start[0]] = input_data[start[0]][:start[1]] + start_pipe(*start) + input_data[start[0]][start[1] + 1:]

    steps = 1
    prev_pos = start
    pos = adjacent_pipe_segment(*start)[0]
    while pos != start:
        adj = adjacent_pipe_segment(*pos)
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
    pass  #TODO
