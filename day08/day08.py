#!/usr/bin/env python3

from pathlib import Path
import re

InputType = tuple[str, dict[str, tuple[str, str]]]
ResultType = int


def load(input_path: Path) -> InputType:
    with open(input_path) as f:
        instructions = f.readline().strip()
        f.readline()  # Discard blank line.
        network_line_regex = re.compile(r"(\w+) = \((\w+), (\w+)\)")
        network = {match.group(1): (match.group(2), match.group(3))
                   for match in map(lambda line: network_line_regex.fullmatch(line.strip()), f.readlines())}
        return instructions, network


def part1(input_data: InputType) -> ResultType:
    current = "AAA"
    steps = 0
    while current != "ZZZ":
        current = input_data[1][current][0 if input_data[0][steps % len(input_data[0])] == "L" else 1]
        steps += 1
    return steps


def part2(input_data: InputType) -> ResultType:
    instructions = [0 if c == "L" else 1 for c in input_data[0]]
    node_list = list(input_data[1].keys())
    # For the matching index in node_list, is this node an end node.
    is_end_node = [True if node.endswith("Z") else False for node in node_list]
    # For the matching index in node_list, what are the left and right connected nodes.
    node_map = [(node_list.index(input_data[1][node][0]), node_list.index(input_data[1][node][1])) for node in node_list]
    ghosts = [node_list.index(node) for node in input_data[1].keys() if node.endswith("A")]
    steps = 0
    instruction_offset = 0
    while True:
        all_at_end = True
        for i in range(len(ghosts)):
            if not is_end_node[ghosts[i]]:
                all_at_end = False
        if all_at_end:
            break
        for i in range(len(ghosts)):
            ghosts[i] = node_map[ghosts[i]][instructions[instruction_offset]]
        steps += 1
        instruction_offset = (instruction_offset + 1) % len(instructions)
    return steps
