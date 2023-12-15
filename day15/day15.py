#!/usr/bin/env python3

from pathlib import Path

InputType = list[str]
ResultType = int


def load(input_path: Path) -> InputType:
    with open(input_path) as f:
        return "".join([line.strip() for line in f.readlines()]).split(",")


def part1(input_data: InputType) -> ResultType:
    def hash_algorithm(s: str) -> int:
        result = 0
        for c in s:
            result += ord(c)
            result = result * 17 % 256
        return result

    return sum(map(hash_algorithm, input_data))


def part2(input_data: InputType) -> ResultType:
    pass  #TODO
