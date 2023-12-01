#!/usr/bin/env python3

import argparse
from pathlib import Path
import sys

InputType = list[str]
ResultType = int


def load(input_path: Path) -> InputType:
    with open(input_path) as f:
        return [line.strip() for line in f.readlines()]


def get_calibration_value(line: str) -> int:
    digit_chars = [c for c in line if c.isdigit()]
    return int(digit_chars[0] + digit_chars[-1])


def part1(input_data: InputType) -> ResultType:
    return sum([get_calibration_value(line) for line in input_data])


def part2(input_data: InputType) -> ResultType:
    pass #TODO


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
