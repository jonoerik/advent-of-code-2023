#!/usr/bin/env python3

import math
from pathlib import Path
import re

# Input is a dictionary of game ids, to games.
# Each game is a list of sets of cubes revealed.
# Cube counts are (red, green, blue).
InputType = dict[int, list[tuple[int, int, int]]]
ResultType = int


def load(input_path: Path) -> InputType:
    def string_to_game_set(s: str) -> tuple[int, int, int]:
        r = 0
        g = 0
        b = 0
        for count, colour in [s1.split(" ") for s1 in s.split(", ")]:
            match colour:
                case "red":
                    r += int(count)
                case "green":
                    g += int(count)
                case "blue":
                    b += int(count)
        return r, g, b

    result: InputType = {}
    line_regex = re.compile(r"Game (?P<game_id>\d+): (?P<games>.*)")

    with open(input_path) as f:
        while line := f.readline().strip():
            match = line_regex.fullmatch(line)
            assert match
            result[int(match.group("game_id"))] = list(map(string_to_game_set, match.group("games").split("; ")))

    return result


def part1(input_data: InputType) -> ResultType:
    max_balls = (12, 13, 14)
    return sum([game_id for game_id, game_sets in input_data.items() if
        all([all([a <= b for a, b in zip(game_set, max_balls)]) for game_set in game_sets])])


def part2(input_data: InputType) -> ResultType:
    def get_min_set(sets: list[tuple[int, int, int]]) -> tuple[int, int, int]:
        return tuple([max(x) for x in zip(*sets)])

    return sum([math.prod(min_set) for min_set in map(get_min_set, input_data.values())])
