#!/usr/bin/env python3

import argparse
from pathlib import Path
import re
import sys

InputType = list[str]
ResultType = int


def load(input_path: Path) -> InputType:
    with open(input_path) as f:
        return [line.strip() for line in f.readlines()]


def part1(input_data: InputType) -> ResultType:
    def get_calibration_value(line: str) -> int:
        digit_chars = [c for c in line if c.isdigit()]
        return int(digit_chars[0] + digit_chars[-1])

    return sum([get_calibration_value(line) for line in input_data])


def part2(input_data: InputType) -> ResultType:
    conversion_map = {str(x): x for x in range(10)} | \
        {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9}
    # "zero" specifically omitted in problem description.
    first_regex = re.compile("|".join(conversion_map.keys()))
    last_regex = re.compile("|".join(conversion_map.keys())[::-1])
    # Need to search from the back of the string with a reversed regex.
    # Can't just use re.split(), as this will miss the last match if it overlaps with a previous match.

    def get_calibration_value(line: str) -> int:
        return (conversion_map[first_regex.search(line).group(0)] * 10) + \
            conversion_map[last_regex.search(line[::-1]).group(0)[::-1]]

    return sum([get_calibration_value(line) for line in input_data])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-1", "--part1", action="store_true")
    parser.add_argument("-2", "--part2", action="store_true")
    parser.add_argument("input")
    args = parser.parse_args()

    if args.part1 == args.part2:
        sys.exit("Exactly one of --part1 or --part2 must be specified.")

    data = load(Path(args.input))
    if args.part1:
        print(part1(data))
    else:  # part2
        print(part2(data))
