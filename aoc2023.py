#!/usr/bin/env python3

import argparse
import importlib
from pathlib import Path
import sys


def run_puzzle(day: int, input_path: Path, part1: bool, **kwargs) -> int | str:
    day_module = importlib.import_module(f"day{day:02}.day{day:02}")
    data = day_module.load(input_path)
    if part1:
        return day_module.part1(data, **kwargs)
    else:
        return day_module.part2(data, **kwargs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-1", "--part1", action="store_true")
    parser.add_argument("-2", "--part2", action="store_true")
    parser.add_argument("day", type=int, help="A number from 1-25 indicating the day of the puzzle to run")
    parser.add_argument("input", type=Path, help="Path to the file containing puzzle input")
    parser.add_argument("-e", "--extra-arg", type=str,
                        help="An extra argument for the puzzle, in the form arg_name=value",
                        action="append", default=[])
    args = parser.parse_args()

    if args.part1 == args.part2:
        sys.exit("Exactly one of --part1 or --part2 must be specified.")
    for ea in args.extra_arg:
        if "=" not in ea:
            sys.exit(f"Extra argument '{ea}' isn't of the form arg_name=value.")
    extra_args = {k: int(v) if v.isdigit() else v for k, v in [i.split("=", 1) for i in args.extra_arg]}

    print(str(run_puzzle(args.day, args.input, args.part1, **extra_args)))
