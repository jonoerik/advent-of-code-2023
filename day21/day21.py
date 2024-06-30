#!/usr/bin/env python3

import abc
import copy
from enum import IntEnum
from pathlib import Path
from typing import Self

InputType = list[str]
ResultType = int


def load(input_path: Path) -> InputType:
    with open(input_path) as f:
        return [line.strip() for line in f.readlines()]


class CellState(IntEnum):
    # Never been ON.
    OFF = 0
    ON = 1
    BLOCKED = 2
    # Was ON last timestep, but OFF now. Only used in part2.
    NEWLY_OFF = 3
    # State transitions:
    # BLOCKED -> BLOCKED
    # OFF -> OFF | ON
    # ON -> NEWLY_OFF
    # NEWLY_OFF -> ON


def part1(input_data: InputType, steps: int = 64) -> ResultType:
    input_data = [[{".": CellState.OFF, "S": CellState.ON, "#": CellState.BLOCKED}[cell] for cell in row]
                  for row in input_data]

    def on_in_neighbourhood(r: int, c: int) -> bool:
        for nr, nc in [(r + dr, c + dc) for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]
                       if 0 <= r + dr < len(input_data) and 0 <= c + dc < len(input_data[0])]:
            if input_data[nr][nc] == CellState.ON:
                return True
        return False

    for _ in range(steps):
        input_data = [[cell if cell == CellState.BLOCKED else
                       (CellState.ON if on_in_neighbourhood(row_index, col_index) else CellState.OFF)
                       for col_index, cell in enumerate(row)] for row_index, row in enumerate(input_data)]

    return sum([row.count(CellState.ON) for row in input_data])


def part2(input_data: InputType, steps: int = 26501365) -> ResultType:
    tile_height = len(input_data)
    tile_width = len(input_data[0])

    class TileInterface(abc.ABC):
        def __init__(self, cells: list[list[CellState]]):
            self._cells = cells

        @abc.abstractmethod
        def cell_on(self, row: int, col: int, current_step: int) -> bool:
            """Return true if the cell in row, col is ON."""
            pass

        @abc.abstractmethod
        def adjacent_tiles_required(self, current_step: int) -> list[tuple[int, int]]:
            """Return a list of tile coordinates, relative to this tile, which could have cells affected by this tile's
            cells. i.e. the tiles with cells adjacent to this tile's ON cells."""
            pass

        @abc.abstractmethod
        def on_cell_count(self, current_step: int) -> int:
            """Return the number of ON cells in this tile."""
            pass

        @abc.abstractmethod
        def calculate_next_state(self, all_tiles: dict[tuple[int, int], Self], current_step: int) -> None:
            """Calculate the next state of this tile, based on its own current state, and the current state of all
            surrounding tiles. This newly calculated state will be made current when advance() is next called."""
            pass

        @abc.abstractmethod
        def advance(self, all_tiles: dict[tuple[int, int], Self]) -> None:
            """Simulate a single step of the puzzle, with ON cells spreading outwards by 1. This state should have
            been pre-calculated by a call to calculate_next_state(). This is necessary, as all tiles, and all cells
            within them must advance simultaneously, rather than advancing one tile, then using that new state in the
            calculation of the adjacent tile's state."""
            pass

        class FilledReplacementStatus(IntEnum):
            # Tile not ready to be replaced by a filled equivalent.
            NO = 0
            # Tile ready to be replaced, even (row+col) tiles are on.
            YES_EVEN = 1
            # Tile ready to be replaced, odd (row+col) tiles are on.
            YES_ODD = 2

        @abc.abstractmethod
        def can_replace_with_filled(self) -> FilledReplacementStatus:
            """Return True if this tile contains a checkerboard of NEWLY_OFF/ON cells, and can therefore be replaced
            with a fixed (i.e. non-simulated tile). For tiles that have already been converted to fixed,
            this will return False, as no replacement is necessary."""
            pass

    class Tile(TileInterface):
        def __init__(self, tile_row: int, tile_col: int, cells: list[list[CellState]]):
            super().__init__(cells)
            self._row = tile_row
            self._col = tile_col
            self._next_cells = None
            self._can_replace_filled = TileInterface.FilledReplacementStatus.NO

        def cell_on(self, row: int, col: int, current_step: int) -> bool:
            return self._cells[row][col] == CellState.ON

        def adjacent_tiles_required(self, current_step: int) -> list[tuple[int, int]]:
            result = []

            if CellState.ON in self._cells[0]:
                result.append((-1, 0))
            if CellState.ON in self._cells[-1]:
                result.append((1, 0))
            if CellState.ON in [row[0] for row in self._cells]:
                result.append((0, -1))
            if CellState.ON in [row[-1] for row in self._cells]:
                result.append((0, 1))

            return result

        def on_cell_count(self, current_step: int) -> int:
            return len([None for row in self._cells for cell in row if cell == CellState.ON])

        def _on_in_neighbourhood(self, r: int, c: int, all_tiles: dict[tuple[int, int], TileInterface],
                                 current_step: int) -> bool:
            for nr, nc in [(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)]:
                tr = self._row

                tc = self._col
                if nr == -1:
                    tr -= 1
                    nr = tile_height - 1
                elif nr == tile_height:
                    tr += 1
                    nr = 0
                elif nc == -1:
                    tc -= 1
                    nc = tile_width - 1
                elif nc == tile_width:
                    tc += 1
                    nc = 0
                if (tr, tc) == (self._row, self._col):
                    if self.cell_on(nr, nc, current_step):
                        return True
                elif (tr, tc) in all_tiles:
                    if all_tiles[(tr, tc)].cell_on(nr, nc, current_step):
                        return True
                else:
                    # Assume all not-yet-existent tiles are full of OFF or BLOCKED cells.
                    # Tiles will be created as soon as any adjacent cells are ON.
                    pass
            return False

        def calculate_next_state(self, all_tiles: dict[tuple[int, int], TileInterface], current_step: int) -> None:
            assert self._next_cells is None
            self._next_cells = [[CellState.BLOCKED if cell == CellState.BLOCKED else
                                 (CellState.NEWLY_OFF if cell == CellState.ON else
                                  (CellState.ON if cell == CellState.NEWLY_OFF else
                                   (CellState.ON if self._on_in_neighbourhood(r, c, all_tiles, current_step) else
                                    CellState.OFF)))
                                 for c, cell in enumerate(row)]
                                for r, row in enumerate(self._cells)]

            if all([self._cells[r][c] == CellState.BLOCKED or
                    self._cells[r][c] == CellState.ON or
                    self._next_cells[r][c] == CellState.ON
                    for r in range(tile_height) for c in range(tile_height)]):
                if all([cell == CellState.ON or cell == CellState.BLOCKED
                        for r, row in enumerate(self._next_cells)
                        for c, cell in enumerate(row) if (r + c) % 2 == 0]):
                    self._can_replace_filled = TileInterface.FilledReplacementStatus.YES_EVEN
                else:
                    self._can_replace_filled = TileInterface.FilledReplacementStatus.YES_ODD
            else:
                self._can_replace_filled = TileInterface.FilledReplacementStatus.NO

        def advance(self, all_tiles: dict[tuple[int, int], TileInterface]) -> None:
            assert self._next_cells is not None
            self._cells = self._next_cells
            self._next_cells = None

        def can_replace_with_filled(self) -> TileInterface.FilledReplacementStatus:
            return self._can_replace_filled

    class FilledTile(TileInterface):
        """A tile where all non-blocked cells are on or off in a strict checkerboard pattern. All cells alternate
        between on and off, and are the opposite state of their immediate neighbours."""

        def __init__(self, cells: list[list[CellState]]):
            """Assumes this tile is being created at step_number == 0."""
            super().__init__(cells)
            assert all([cell == CellState.BLOCKED or cell == CellState.ON
                        for r, row in enumerate(self._cells)
                        for c, cell in enumerate(row)
                        if (r + c) % 2 == 0]) or \
                   all([cell == CellState.BLOCKED or cell == CellState.ON
                        for r, row in enumerate(self._cells)
                        for c, cell in enumerate(row)
                        if (r + c) % 2 == 1])

        def cell_on(self, row: int, col: int, current_step: int) -> bool:
            return self._cells[row][col] == CellState.ON if current_step % 2 == 0 \
                else self._cells[row][col] == CellState.NEWLY_OFF

        def adjacent_tiles_required(self, current_step: int) -> list[tuple[int, int]]:
            # By the time a tile has been completely filled, all adjacent tiles should already have been instantiated.
            return []

        def on_cell_count(self, current_step: int) -> int:
            required_state = CellState.ON if current_step % 2 == 0 else CellState.NEWLY_OFF
            return len([None for row in self._cells for cell in row if cell == required_state])

        def calculate_next_state(self, all_tiles: dict[tuple[int, int], TileInterface], current_step: int) -> None:
            pass

        def advance(self, all_tiles: dict[tuple[int, int], TileInterface]) -> None:
            pass

        def can_replace_with_filled(self) -> TileInterface.FilledReplacementStatus:
            return TileInterface.FilledReplacementStatus.NO

    def is_easy_solve() -> bool:
        """For this puzzle to be easily solvable for large step counts, the input must be a square of an odd width and
        height, with 'S' centred directly in the middle, a perimeter of "." around the edges, and direct paths of "."
        from S out to each edge."""
        if tile_height != tile_width:
            return False
        if tile_height % 2 != 1 or tile_width % 2 != 1:
            return False
        for row in [0, tile_height // 2, tile_height - 1]:
            if "#" in input_data[row]:
                return False
        for col in [0, tile_width // 2, tile_width - 1]:
            if "#" in [row[col] for row in input_data]:
                return False
        if input_data[tile_height // 2][tile_width // 2] != "S":
            return False
        return True

    def easy_solve() -> int:
        pass  # TODO

    def naive_solve() -> int:
        start_tile_cells = [[{".": CellState.OFF, "S": CellState.OFF, "#": CellState.BLOCKED}[cell] for cell in row]
                            for row in input_data]
        tiles: dict[tuple[int, int], TileInterface] = \
            {(0, 0): Tile(0, 0, [[{".": CellState.OFF, "S": CellState.ON, "#": CellState.BLOCKED}[cell] for cell in row]
                                 for row in input_data])}
        filled_tile_even = FilledTile([[CellState.BLOCKED if cell == CellState.BLOCKED else
                                        (CellState.ON if (r+c) % 2 == 0 else CellState.NEWLY_OFF)
                                        for c, cell in enumerate(row)]
                                       for r, row in enumerate(start_tile_cells)])
        filled_tile_odd = FilledTile([[CellState.BLOCKED if cell == CellState.BLOCKED else
                                      (CellState.ON if (r + c) % 2 == 1 else CellState.NEWLY_OFF)
                                      for c, cell in enumerate(row)]
                                     for r, row in enumerate(start_tile_cells)])

        step_number = 0
        while step_number < steps:
            # For each tile, if cells at edges are on and no tile is adjacent, create the adjacent tile.
            new_tiles = set()
            for (tr, tc), tile in tiles.items():
                for dr, dc in tile.adjacent_tiles_required(step_number):
                    if (tr+dr, tc+dc) not in tiles:
                        new_tiles.add((tr+dr, tc+dc))
            for tr, tc in new_tiles:
                tiles[(tr, tc)] = Tile(tr, tc, copy.deepcopy(start_tile_cells))

            for tile in tiles.values():
                tile.calculate_next_state(tiles, step_number)
            for tile in tiles.values():
                tile.advance(tiles)

            step_number += 1

            for tile_pos, tile in tiles.items():
                replace_status = tile.can_replace_with_filled()
                if replace_status == TileInterface.FilledReplacementStatus.YES_EVEN:
                    tiles[tile_pos] = filled_tile_even if step_number % 2 == 0 else filled_tile_odd
                elif replace_status == TileInterface.FilledReplacementStatus.YES_ODD:
                    tiles[tile_pos] = filled_tile_odd if step_number % 2 == 0 else filled_tile_even

        return sum([tile.on_cell_count(step_number) for tile in tiles.values()])

    if is_easy_solve():
        return easy_solve()
    else:
        return naive_solve()
