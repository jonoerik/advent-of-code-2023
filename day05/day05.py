#!/usr/bin/env python3

from pathlib import Path
import re
from typing import Self

# (destination range start, source range start, range length)
SingleMappingType = tuple[int, int, int]
# (source name, target name, list of mappings)
MapType = tuple[str, str, list[SingleMappingType]]
# (list of seeds, list of mappings)
InputType = tuple[list[int], list[MapType]]
ResultType = int


def load(input_path: Path) -> InputType:
    seeds: list[int]
    maps = []
    seeds_regex = re.compile(r"seeds: (.*)")
    map_heading_regex = re.compile(r"(\w+)-to-(\w+) map:")

    with open(input_path) as f:
        seeds_match = seeds_regex.fullmatch(f.readline().strip())
        assert seeds_match
        seeds = [int(x) for x in seeds_match.group(1).split()]
        f.readline().strip()  # Blank line

        while f:
            heading_match = map_heading_regex.fullmatch(f.readline().strip())
            if not heading_match:
                break
            source_name = heading_match.group(1)
            target_name = heading_match.group(2)
            sub_mappings = []
            while line := f.readline().strip():
                sub_mappings.append(tuple([int(x) for x in line.split()]))
            maps.append((source_name, target_name, sub_mappings))

    return seeds, maps


def part1(input_data: InputType) -> ResultType:
    def apply_map(start_val: int, mapping: MapType) -> int:
        for mapping_line in mapping[2]:
            if mapping_line[1] <= start_val < mapping_line[1] + mapping_line[2]:
                return start_val - mapping_line[1] + mapping_line[0]
        return start_val

    def seed_to_location(seed: int) -> int:
        current = seed
        for mapping in input_data[1]:
            current = apply_map(current, mapping)
        return current

    return min(map(seed_to_location, input_data[0]))


def part2(input_data: InputType) -> ResultType:
    class Range:
        """
        A range of numbers [start, end).
        For convenience, ranges may be of zero length (start == end), covering no numbers.
        """
        def __init__(self, start: int, end: int) -> None:
            self.start: int = start
            self.end: int = end

        def shift(self, x: int) -> None:
            self.start += x
            self.end += x

        def __bool__(self):
            return self.start != self.end

        def intersection(self, other: Self) -> Self:
            if other.start < self.start:
                if other.end > self.start:
                    return Range(self.start, min(self.end, other.end))
                else:
                    return Range(0, 0)
            elif self.start <= other.start < self.end:
                return Range(other.start, min(self.end, other.end))
            else:
                return Range(0, 0)

        def sub(self, other: Self) -> list[Self]:
            """
            'Subtract'.
            Remove all points in other from this range, and return the resulting ranges (0, 1, or 2).
            """
            if not self.intersection(other):
                return [Range(self.start, self.end)]
            elif other.start <= self.start <= self.end <= other.end:
                return []
            elif other.start <= self.start < other.end < self.end:
                return [Range(other.end, self.end)]
            elif self.start < other.start < self.end <= other.end:
                return [Range(self.start, other.start - 1)]
            elif self.start < other.start <= other.end < self.end:
                return [Range(self.start, other.start - 1), Range(other.end, self.end)]
            else:
                assert False

    class RangeList:
        """
        RangeLists may contain repeated ranges, overlapping ranges, and zero-length ranges.
        These shouldn't affect the result, and getting rid of them is a lot of extra work.
        """
        def __init__(self, rl: list[Range]) -> None:
            self.ranges: list[Range] = rl

        def intersections(self, other: Range) -> Self:
            result = RangeList([])
            for r in self.ranges:
                intersection = r.intersection(other)
                if intersection:
                    result.add(intersection)
            return result

        def remove(self, other: Range) -> None:
            new_ranges: list[Range] = []
            for r in self.ranges:
                new_ranges += r.sub(other)
            self.ranges = new_ranges

        def add(self, other: Range) -> None:
            self.ranges.append(other)

        def min(self) -> int:
            return min([r.start for r in self.ranges if r])

    seeds = [Range(start, start + length) for start, length in zip(input_data[0][0::2], input_data[0][1::2])]

    def apply_map(rl: RangeList, mapping: MapType) -> RangeList:
        """
        Note: this destructively modifies parameter rl.
        """
        new_rl = RangeList([])
        for mapping_line in mapping[2]:
            mapping_line_range = Range(mapping_line[1], mapping_line[1] + mapping_line[2])
            intersections = rl.intersections(mapping_line_range)
            for intersection in intersections.ranges:
                rl.remove(intersection)
                intersection.shift(mapping_line[0] - mapping_line[1])
                new_rl.add(intersection)
        for remainder in rl.ranges:
            new_rl.add(remainder)
        return new_rl

    def seeds_to_location(r: Range) -> RangeList:
        current = RangeList([r])
        for mapping in input_data[1]:
            current = apply_map(current, mapping)
        return current

    return min([locations.min() for locations in map(seeds_to_location, seeds)])
