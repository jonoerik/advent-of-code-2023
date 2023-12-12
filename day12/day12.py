#!/usr/bin/env python3

import math
import multiprocessing
from pathlib import Path
import re

InputType = list[tuple[str, list[int]]]
ResultType = int


def load(input_path: Path) -> InputType:
    def parse_line(s: str) -> tuple[str, list[int]]:
        a, b = s.split(" ")
        return a, [int(x) for x in b.split(",")]
    with open(input_path) as f:
        return [parse_line(line.strip()) for line in f.readlines()]


all_dots_regex = re.compile(r"^(?:\.+|$)")
all_unknown_regex = re.compile(r"^(\?+)(?:\.+|$)")
region_start_known_regex = re.compile(r"^(#[#?]*)(?:\.+|$)")
region_start_unknown_regex = re.compile(r"^(\?[#?]*)(?:\.+|$)")

# Easier than region_start_unknown.
easy_reversed_regex = re.compile(r"(?:\.|#|(?:^|\.)\?+)$")
# Only easier if there are fewer "?" at the end of the string than at the start.
easyish_reversed_regex = re.compile(r"#(\?+)$")


def possible_layouts(s: str, groups: list[int]) -> int:
    if len(groups) == 0:
        if "#" in s:
            # Run out of groups for remaining '#' in s.
            return 0
        else:
            # Remaining '?' in s must be '.'.
            return 1
    if len(s) == 0:
        # Run out of s to fit remaining groups into.
        return 0

    if match := all_dots_regex.match(s):
        # Skip '.'s.
        return possible_layouts(s[len(match.group(0)):], groups)

    if match := all_unknown_regex.match(s):
        total = possible_layouts(s[len(match.group(0)):], groups)
        for i in range(1, len(groups) + 1):
            if sum(groups[:i]) + i - 1 <= len(match.group(1)):
                # Amount of extra space in this region, beyond what's required to fit the first i groups.
                slack_space = len(match.group(1)) - sum(groups[:i]) - i + 1
                # The number of ways to distribute slack_space spaces around i groups (i.e. in i + 1 different places)
                # is equal to
                #     len(combinations_with_replacement(i + 1 different items, slack_space))
                # i.e.
                #     ((i+1) + slack_space - 1)! / slack_space! / ((i+1) - 1)!
                # https://docs.python.org/3/library/itertools.html#itertools.combinations_with_replacement
                possible_positionings = math.factorial(i + slack_space) // math.factorial(slack_space) // math.factorial(i)
                total += possible_layouts(s[len(match.group(0)):], groups[i:]) * possible_positionings
        return total

    if match := region_start_known_regex.match(s):
        if len(match.group(1)) >= groups[0]:
            if len(s) > groups[0] and s[groups[0]] == '#':
                # Next group can't be exactly the right size.
                return 0
            else:
                # Match a single group.
                return possible_layouts(s[groups[0] + 1:], groups[1:])
        else:
            # Not enough '#' and '?' for the next group.
            return 0

    if match := region_start_unknown_regex.match(s):
        if len(match.group(1)) >= groups[0]:
            if len(s) > groups[0] and s[groups[0]] == '#':
                # Can't use this '?' as '#', as next group wouldn't be exactly the right size.
                return possible_layouts(s[1:], groups)
            else:
                # This case is the most recursive, as it involves 2 recursive calls, one of which only consumes 1
                # character from s and no groups elements.
                # Therefore, check if there is an easier to handle case by reversing both s and groups (which doesn't
                # alter the result of this function) and working from the other end.
                if easy_reversed_regex.search(s):
                    # Reversed version has a much easier first match.
                    return possible_layouts(s[::-1], groups[::-1])
                elif reversed_match := easyish_reversed_regex.search(s):
                    # Reversed version also falls into the group_start_unknown_regex category, but the distance to the
                    # first '#' is shorter, so it should be a better option to solve.
                    if len(reversed_match.group(1)) < s.index("#"):
                        return possible_layouts(s[::-1], groups[::-1])

                # Try replacing the last "?" before the first "#" with either "." or "#".
                # e.g. ????##?. -> ???###?. or ???.##?.
                # This breaks down into fewer recursive paths than trying both possibilities of s[0].
                first_hash_index = s.index("#")
                assert s[first_hash_index - 1] == "?"
                return possible_layouts(s[:first_hash_index-1] + "#" + s[first_hash_index:], groups) + \
                    possible_layouts(s[:first_hash_index - 1] + "." + s[first_hash_index:], groups)

        else:
            # Not enough '#' and '?' for the next group.
            if '#' in match.group(1):
                return 0
            else:
                return possible_layouts(s[len(match.group(0)):], groups)

    assert False  # The given regexes should catch all cases of s.


def part1(input_data: InputType) -> ResultType:
    with multiprocessing.Pool() as pool:
        return sum(pool.starmap(possible_layouts, input_data))


def part2(input_data: InputType) -> ResultType:
    input_data = [("?".join([s] * 5), g * 5) for s, g in input_data]
    return part1(input_data)
