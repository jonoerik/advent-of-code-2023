#!/usr/bin/env python3

import math
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
    class Ghost:
        def __init__(self, start_node: str):
            def find_loop() -> None:
                """
                Find the point at which this ghost starts repeating its path, and the length of that loop.
                """
                # Dictionary from (instructions_offset, node) to the number of steps it first took to reach that state.
                memo: dict[tuple[int, str], int] = {(0, start_node): 0}
                steps = 0
                instructions_offset = 0
                node = start_node
                while True:
                    node = input_data[1][node][0 if input_data[0][instructions_offset] == "L" else 1]
                    steps += 1
                    instructions_offset = (instructions_offset + 1) % len(input_data[0])
                    if (instructions_offset, node) in memo:
                        break
                    else:
                        memo[(instructions_offset, node)] = steps

                # Number of steps after which the ghost starts looping (traversing the same cycle of nodes repeatedly).
                self.loop_start: int = memo[(instructions_offset, node)]
                # Length of the loop.
                self.loop_length: int = steps - self.loop_start
            find_loop()

            def run_length_encode_path(start: int, length: int) -> list[tuple[int, bool]]:
                """
                Create a run-length encoded version of this ghost's path, noting only whether at each point the ghost
                is on end or non-end node.
                Run-length encoded paths are a list of (length, is_end_node).
                e.g. [(4, False), (2, True), (10, False)] is a path of 4 non-end nodes, 2 end, nodes, then 10 non-end
                nodes.
                """
                result: list[tuple[int, bool]] = []
                node = start_node
                instructions_offset = 0
                for i in range(start):
                    node = input_data[1][node][0 if input_data[0][instructions_offset] == "L" else 1]
                    instructions_offset = (instructions_offset + 1) % len(input_data[0])
                for i in range(length):
                    on_end = node.endswith("Z")
                    if len(result) == 0 or result[-1][1] != on_end:
                        result.append((1, on_end))
                    else:
                        result[-1] = (result[-1][0] + 1, on_end)
                    # Move to next node.
                    node = input_data[1][node][0 if input_data[0][instructions_offset] == "L" else 1]
                    instructions_offset = (instructions_offset + 1) % len(input_data[0])
                return result

            self.initial_path = run_length_encode_path(0, self.loop_start)
            self.loop_path = run_length_encode_path(self.loop_start, self.loop_length)

            if len(self.loop_path) >= 2 and self.loop_path[0][1] == self.loop_path[-1][1]:
                # Can simplify loop path by copying the first segment into the initial path, and moving that first loop
                # segment to the end of the loop, combining it with the last segment.
                if self.loop_path[0][1] == self.initial_path[-1][1]:
                    self.initial_path[-1] = (self.initial_path[-1][0] + self.loop_path[0][0], self.initial_path[-1][1])
                else:
                    self.initial_path.append(self.loop_path[0])
                self.loop_path[-1] = (self.loop_path[-1][0] + self.loop_path[0][0], self.loop_path[-1][1])
                self.loop_path.pop(0)

            # A ghost is simple if its loop path is 1 end node, and a single sequence of non-end nodes.
            # i.e. self.loop_path == [(1, True), (_, False)]
            # Simple ghosts are easy to combine with other ghosts at the point in time when they're both
            # on their end nodes.
            # This seems to cover all ghosts in my input file.
            self.is_simple = len(self.loop_path) == 2 and self.loop_path[0][0] == 1 and \
                self.loop_path[0][1] and not self.loop_path[1][1]

            # True if this ghost is in initial_path, False if the ghost is in loop_path.
            self.is_in_initial = True
            # Index within the path of the current segment.
            self.current_segment_index = 0
            # Offset within the current segment.
            self.current_segment_offset = 0

        def current_segment(self) -> tuple[int, bool]:
            if self.is_in_initial:
                return self.initial_path[self.current_segment_index]
            else:
                return self.loop_path[self.current_segment_index]

        def increment_segment(self) -> None:
            self.current_segment_index += 1
            if self.current_segment_index >= len(self.initial_path if self.is_in_initial else self.loop_path):
                self.is_in_initial = False
                self.current_segment_index = 0

        def segment_remaining(self) -> int:
            return self.current_segment()[0] - self.current_segment_offset

        def run_steps(self, distance: int) -> None:
            """
            Run this ghost for the specified distance (number of steps), updating is_in_initial, current_segment, and
            current_segment_offset.
            """
            while distance > 0:
                if distance >= self.segment_remaining():
                    distance -= self.segment_remaining()
                    self.increment_segment()
                    self.current_segment_offset = 0
                else:
                    self.current_segment_offset += distance
                    distance = 0

        def is_on_end(self) -> bool:
            return self.current_segment()[1]

    def merge_ghosts(a: Ghost, b: Ghost) -> None:
        """
        Merge ghost b into ghost a.
        """
        for ghost in [a, b]:
            assert not ghost.is_in_initial and ghost.is_simple and ghost.is_on_end()
            assert ghost.current_segment_index == 0 and ghost.current_segment_offset == 0
        a.loop_length = math.lcm(a.loop_length, b.loop_length)
        a.loop_path = [(1, True), (a.loop_length - 1, False)]

    ghosts = [Ghost(node) for node in input_data[1].keys() if node.endswith("A")]
    steps = 0
    while not all([ghost.is_on_end() for ghost in ghosts]):
        while len(to_merge := [i for i, ghost in enumerate(ghosts)
                               if ghost.is_simple and not ghost.is_in_initial and ghost.is_on_end()][:2]) >= 2:
            # 2 simple ghosts are both on their end node, and can be merged into a single ghost.
            merge_ghosts(ghosts[to_merge[0]], ghosts[to_merge[1]])
            del ghosts[to_merge[1]]

        run_distance = max([ghost.segment_remaining() for ghost in ghosts if not ghost.is_on_end()])
        for ghost in ghosts:
            ghost.run_steps(run_distance)
        steps += run_distance

    return steps
