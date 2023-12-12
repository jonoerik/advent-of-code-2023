#!/usr/bin/env python3

from pathlib import Path

InputType = list[tuple[str, list[int]]]
ResultType = int


def load(input_path: Path) -> InputType:
    def parse_line(s: str) -> tuple[str, list[int]]:
        a, b = s.split(" ")
        return a, [int(x) for x in b.split(",")]
    with open(input_path) as f:
        return [parse_line(line.strip()) for line in f.readlines()]


def part1(input_data: InputType) -> ResultType:
    def check_layout(s: str, groups: list[int]) -> bool:
        return [len(g) for g in s.split(".") if len(g) > 0] == groups

    def possible_layouts(s: str, groups: list[int]) -> int:
        if "?" not in s:
            if check_layout(s, groups):
                return 1
            else:
                return 0

        unknown_index = s.index("?")
        return sum([possible_layouts(s[:unknown_index] + x + s[unknown_index + 1:], groups) for x in [".", "#"]])

    return sum(map(lambda x: possible_layouts(*x), input_data))


def part2(input_data: InputType) -> ResultType:
    pass  #TODO
