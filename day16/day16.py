#!/usr/bin/env python3

from enum import Enum
from pathlib import Path
import typing

InputType = list[str]
ResultType = int


def load(input_path: Path) -> InputType:
    with open(input_path) as f:
        return [line.strip() for line in f.readlines()]


class BeamDirection(Enum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3


class Beam(typing.NamedTuple):
    row: int
    col: int
    direction: BeamDirection

    def target_row(self) -> int:
        return self.row - 1 if self.direction == BeamDirection.UP else \
            (self.row + 1 if self.direction == BeamDirection.DOWN else self.row)

    def target_col(self) -> int:
        return self.col - 1 if self.direction == BeamDirection.LEFT else \
            (self.col + 1 if self.direction == BeamDirection.RIGHT else self.col)


def energised_tiles(input_data: InputType, starting_beam: Beam) -> int:
    beams = [starting_beam]
    beam_history = {starting_beam}
    energised = [[False for col in range(len(input_data[0]))] for row in range(len(input_data))]

    while beams:
        next_beams = []
        for beam in beams:
            target_row = beam.target_row()
            target_col = beam.target_col()
            # Only deal with beams that aren't leaving the contraption area.
            if (0 <= target_row < len(input_data)) and (0 <= target_col < len(input_data[0])):
                match input_data[target_row][target_col]:
                    case ".":
                        next_beams.append(Beam(target_row, target_col, beam.direction))
                    case "/":
                        next_beams.append(Beam(target_row, target_col, {
                            BeamDirection.UP: BeamDirection.RIGHT,
                            BeamDirection.RIGHT: BeamDirection.UP,
                            BeamDirection.DOWN: BeamDirection.LEFT,
                            BeamDirection.LEFT: BeamDirection.DOWN,
                        }[beam.direction]))
                    case "\\":
                        next_beams.append(Beam(target_row, target_col, {
                            BeamDirection.UP: BeamDirection.LEFT,
                            BeamDirection.RIGHT: BeamDirection.DOWN,
                            BeamDirection.DOWN: BeamDirection.RIGHT,
                            BeamDirection.LEFT: BeamDirection.UP,
                        }[beam.direction]))
                    case "|":
                        match beam.direction:
                            case BeamDirection.UP | BeamDirection.DOWN:
                                next_beams.append(Beam(target_row, target_col, beam.direction))
                            case BeamDirection.LEFT | BeamDirection.RIGHT:
                                next_beams.append(Beam(target_row, target_col, BeamDirection.UP))
                                next_beams.append(Beam(target_row, target_col, BeamDirection.DOWN))
                    case "-":
                        match beam.direction:
                            case BeamDirection.UP | BeamDirection.DOWN:
                                next_beams.append(Beam(target_row, target_col, BeamDirection.LEFT))
                                next_beams.append(Beam(target_row, target_col, BeamDirection.RIGHT))
                            case BeamDirection.LEFT | BeamDirection.RIGHT:
                                next_beams.append(Beam(target_row, target_col, beam.direction))

        # Skip beams that we've seen before.
        beams = [beam for beam in next_beams if beam not in beam_history]
        for beam in beams:
            energised[beam.row][beam.col] = True
        beam_history.update(beams)

    return sum([1 if cell else 0 for row in energised for cell in row])


def part1(input_data: InputType) -> ResultType:
    return energised_tiles(input_data, Beam(0, -1, BeamDirection.RIGHT))


def part2(input_data: InputType) -> ResultType:
    return max(energised_tiles(input_data, beam) for beam in
               [Beam(row, col, direction) for row in range(len(input_data))
                for col, direction in [(-1, BeamDirection.RIGHT), (len(input_data[0]), BeamDirection.LEFT)]] +
               [Beam(row, col, direction) for col in range(len(input_data[0]))
                for row, direction in [(-1, BeamDirection.DOWN), (len(input_data), BeamDirection.UP)]])
