#!/usr/bin/env python3

from pathlib import Path
import re

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
    pass  #TODO
