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

    # Use zip(*image) to transpose image, swapping rows for columns.
    return sum([sum(v_reflections(image)) + 100 * sum(v_reflections([list(row) for row in zip(*image)]))
                for image in input_data])


def part2(input_data: InputType) -> ResultType:
    def v_reflection_errors(image: SingleImageType, i: int) -> int:
        """Return the number of characters that don't match in a reflection in image between columns i-1 and i."""
        return sum([sum([1 if x != y else 0 for x, y in zip(a, b)])
                    for a, b in [(line[i-1::-1], line[i:])for line in image]])

    def v_smudged_reflection(image: SingleImageType) -> int:
        """Return the index of a smudged vertical reflection in image, or 0 if none found."""
        for i in range(1, len(image[0])):
            if v_reflection_errors(image, i) == 1:
                return i
        return 0

    # Use zip(*image) to transpose image, swapping rows for columns.
    return sum([v_smudged_reflection(image) or 100 * v_smudged_reflection([list(row) for row in zip(*image)])
                for image in input_data])
