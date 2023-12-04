#!/usr/bin/env python3

from pathlib import Path
import re

# Dictionary from game number to (winning numbers, your numbers)
InputType = dict[int, tuple[set[int], set[int]]]
ResultType = int


def load(input_path: Path) -> InputType:
    line_regex = re.compile(r"Card +(?P<game_num>\d+):(?P<winning>[0-9 ]+)\|(?P<yours>[0-9 ]+)")

    def parse_line(line: str) -> tuple[int, set[int], set[int]]:
        match = line_regex.fullmatch(line.strip())
        return int(match.group("game_num")), \
            set([int(x) for x in match.group("winning").split()]), \
            set([int(x) for x in match.group("yours").split()])

    with open(input_path) as f:
        return {game_num: (winning, yours) for game_num, winning, yours in map(parse_line, f.readlines())}


def part1(input_data: InputType) -> ResultType:
    def card_value(winning: set[int], yours: set[int]) -> int:
        winning_numbers = len(yours.intersection(winning))
        return 0 if winning_numbers == 0 else 2 ** (winning_numbers - 1)

    return sum([card_value(w, y) for w, y in input_data.values()])


def part2(input_data: InputType) -> ResultType:
    pass  #TODO
