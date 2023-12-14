#!/usr/bin/env python3

from collections.abc import Iterator
from pathlib import Path

SingleImageType = list[list[bool]]
InputType = list[SingleImageType]
ResultType = int


def load(input_path: Path) -> InputType:
    result = [[]]
    with open(input_path) as f:
        for line in f.readlines():
            line = line.strip()
            if not line:
                result.append([])
            else:
                result[len(result)-1].append([c == "#" for c in line])
    return result


def part1(input_data: InputType) -> ResultType:
    def is_v_reflection(image: SingleImageType, i: int) -> bool:
        """Return True iff a line of reflection exists in image between columns i-1 and i."""
        for a, b in [(line[i-1::-1], line[i:]) for line in image]:
            if a[:len(b)] != b[:len(a)]:
                return False
        return True

    def v_reflections(image: SingleImageType) -> Iterator[int]:
        """Generator function returning the indexes of vertical lines of reflection."""
        for i in range(1, len(image[0])):
            if is_v_reflection(image, i):
                yield i

    def is_h_reflection(image: SingleImageType, i: int) -> bool:
        """Return True iff a line of reflection exists in image between rows i-1 and i."""
        for col in range(0, len(image[0])):
            a = [row[col] for row in image][i-1::-1]
            b = [row[col] for row in image][i:]
            if a[:len(b)] != b[:len(a)]:
                return False
        return True

    def h_reflections(image: SingleImageType) -> Iterator[int]:
        """Generator function returning the indexes of horizontal lines of reflection."""
        for i in range(1, len(image)):
            if is_h_reflection(image, i):
                yield i

    return sum([sum(v_reflections(image)) + 100 * sum(h_reflections(image)) for image in input_data])


def part2(input_data: InputType) -> ResultType:
    pass  #TODO
