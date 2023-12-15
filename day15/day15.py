#!/usr/bin/env python3

from pathlib import Path
import re
import sys

InputType = list[str]
ResultType = int


def load(input_path: Path) -> InputType:
    with open(input_path) as f:
        return "".join([line.strip() for line in f.readlines()]).split(",")


def hash_algorithm(s: str) -> int:
    result = 0
    for c in s:
        result += ord(c)
        result = result * 17 % 256
    return result


def part1(input_data: InputType) -> ResultType:
    return sum(map(hash_algorithm, input_data))


def part2(input_data: InputType) -> ResultType:
    step_regex = re.compile(r"([a-z]+)(-|=\d+)")
    # Parse input data to a list of (lens_label, target_box, True=remove_lens False=add/replace_lens, focal_length).
    input_data = [(match.group(1), hash_algorithm(match.group(1)), match.group(2)[0] == "-",
                   int(match.group(2)[1:]) if match.group(2)[0] == "=" else None)
                  for match in map(step_regex.fullmatch, input_data)]
    # Dicts are insertion ordered as of Python 3.7, which we'll rely on to keep lenses ordered in our boxes.
    # First-inserted element will be the front-most lens in each box.
    assert sys.version_info >= (3, 7)
    boxes = [dict() for _ in range(256)]

    for lens_label, box_index, is_removal, focal_length in input_data:
        if is_removal:
            boxes[box_index].pop(lens_label, None)
        else:
            boxes[box_index][lens_label] = focal_length

    return sum((box_index+1) * (lens_index+1) * focal_length for box_index, box in enumerate(boxes)
               for lens_index, focal_length in enumerate(box.values()))
