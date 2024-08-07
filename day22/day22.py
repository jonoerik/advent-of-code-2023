#!/usr/bin/env python3

import collections
from pathlib import Path
import re
from typing import Self

CoordType = tuple[int, int, int]
InputType = list[tuple[CoordType, CoordType]]
ResultType = int


def load(input_path: Path) -> InputType:
    line_regex = re.compile(r"^(\d+),(\d+),(\d+)~(\d+),(\d+),(\d+)$")
    with open(input_path) as f:
        return [((int(match.group(1)), int(match.group(2)), int(match.group(3))),
                 (int(match.group(4)), int(match.group(5)), int(match.group(6))))
                for match in [line_regex.fullmatch(line.strip()) for line in f.readlines()]]


class Block:
    def __init__(self, start: CoordType, end: CoordType):
        self._start = start
        self._end = end
        assert all([start[i] <= end[i] for i in range(3)])
        assert start[2] > 0 and end[2] > 0

    def __repr__(self) -> str:
        return f"Block({self._start}, {self._end})"

    def min_z(self) -> int:
        return self._start[2]

    def max_z(self) -> int:
        return self._end[2]

    def collides(self, other: Self) -> bool:
        """Return true if this block and other overlap."""
        for dim in range(3):
            if self._end[dim] < other._start[dim] or self._start[dim] > other._end[dim]:
                return False
        return True

    def supports(self, other: Self) -> bool:
        """Return true if this block is not overlapping with other, but is directly beneath it, supporting other."""
        if self._end[2] + 1 != other._start[2]:
            return False
        for dim in range(2):
            if self._end[dim] < other._start[dim] or self._start[dim] > other._end[dim]:
                return False
        return True

    def shadow(self) -> Self:
        """Get the block representing the space directly underneath this block, or None if the block is on the
        ground."""
        if self.min_z() <= 1:
            return None
        return Block((self._start[0], self._start[1], 1), (self._end[0], self._end[1], self._start[2] - 1))

    def lowered(self, z: int) -> Self:
        """Return this block, but lowered to a min_z of z"""
        dz = z - self._start[2]
        return Block((self._start[0], self._start[1], self._start[2] + dz),
                     (self._end[0], self._end[1], self._end[2] + dz))


def collapse(blocks: list[Block]) -> list[Block]:
    """Simulate falling of blocks, and return the final rest state."""
    fallen = []
    for b in sorted(blocks, key=Block.min_z):
        b_shadow = b.shadow()
        z = max([1] + [b2.max_z() + 1 for b2 in fallen if b2.collides(b_shadow)]) if b_shadow else 1
        fallen.append(b.lowered(z))
    return fallen


def part1(input_data: InputType) -> ResultType:
    fallen = collapse([Block(*input_block) for input_block in input_data])

    # For each block, establish which blocks support it.
    z_maxs: dict[int, list[Block]] = collections.defaultdict(list)
    for b in fallen:
        z_maxs[b.max_z()].append(b)
    supported_by = {b: [b2 for b2 in z_maxs[b.min_z() - 1] if b2.supports(b)] for b in fallen}

    return len([None for b in fallen if [b] not in supported_by.values()])


def part2(input_data: InputType) -> ResultType:
    fallen = collapse([Block(*input_block) for input_block in input_data])

    # For each block, establish which blocks it's supporting.
    z_mins: dict[int, list[Block]] = collections.defaultdict(list)
    for b in fallen:
        z_mins[b.min_z()].append(b)
    supports = {b: [b2 for b2 in z_mins[b.max_z() + 1] if b.supports(b2)] for b in fallen}

    ground_blocks = [b for b in fallen if b.min_z() <= 1]

    def blocks_supported(removed_block: Block) -> int:
        """Return the number of blocks still supported by the ground, if removed_block were to be removed."""
        to_process = set(ground_blocks)
        to_process.discard(removed_block)
        reachable = set()
        while to_process:
            current = to_process.pop()
            reachable.add(current)
            for next_block in supports[current]:
                if next_block not in reachable and next_block is not removed_block:
                    to_process.add(next_block)
        return len(reachable)

    total_blocks = len(fallen)
    return sum([total_blocks - blocks_supported(b) - 1 for b in fallen])
