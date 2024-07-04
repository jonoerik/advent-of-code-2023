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


def part1(input_data: InputType, steps: int = 64) -> ResultType:
    class CellState(IntEnum):
        OFF = 0
        ON = 1
        BLOCKED = 2

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

    class CellState(IntEnum):
        # Never been ON.
        OFF = 0
        # First turned ON during an even timestep (or ON at start). Will be ON during other even timesteps.
        ON_EVEN = 1
        # First turned ON during an odd timestep. Will be ON during other odd timesteps.
        ON_ODD = 2
        BLOCKED = 3

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
        def advance(self, all_tiles: dict[tuple[int, int], Self], current_step: int) -> None:
            """Advance to the next state of this tile, based on its current state, and the current state of all
            surrounding tiles."""
            pass

        class FilledReplacementStatus(IntEnum):
            # Tile not ready to be replaced by a filled equivalent.
            NO = 0
            # Tile ready to be replaced, even (row+col) tiles are ON_EVEN.
            YES_EVEN = 1
            # Tile ready to be replaced, even (row+col) tiles are ON_ODD.
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
            self._on_even_cells = set([(r, c) for r, row in enumerate(self._cells) for c, cell in enumerate(row)
                                       if cell == CellState.ON_EVEN])
            self._on_odd_cells = set([(r, c) for r, row in enumerate(self._cells) for c, cell in enumerate(row)
                                      if cell == CellState.ON_ODD])
            self._off_cells = set([(r, c) for r, row in enumerate(self._cells) for c, cell in enumerate(row)
                                   if cell == CellState.OFF])

        def cell_on(self, row: int, col: int, current_step: int) -> bool:
            return (row, col) in self._on_even_cells if current_step % 2 == 0 else (row, col) in self._on_odd_cells

        def adjacent_tiles_required(self, current_step: int) -> list[tuple[int, int]]:
            result = []

            if any([cell in [CellState.ON_EVEN, CellState.ON_ODD] for cell in self._cells[0]]):
                result.append((-1, 0))
            if any([cell in [CellState.ON_EVEN, CellState.ON_ODD] for cell in self._cells[-1]]):
                result.append((1, 0))
            if any([row[0] in [CellState.ON_EVEN, CellState.ON_ODD] for row in self._cells]):
                result.append((0, -1))
            if any([row[-1] in [CellState.ON_EVEN, CellState.ON_ODD] for row in self._cells]):
                result.append((0, 1))

            return result

        def on_cell_count(self, current_step: int) -> int:
            return len(self._on_even_cells) if current_step % 2 == 0 else len(self._on_odd_cells)

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

        def advance(self, all_tiles: dict[tuple[int, int], TileInterface], current_step: int) -> None:
            # ON_ODD and ON_EVEN are swapped here, as we're calculating the state for the next step.
            next_state = CellState.ON_ODD if current_step % 2 == 0 else CellState.ON_EVEN
            to_remove = set()
            for r, c in self._off_cells:
                if self._on_in_neighbourhood(r, c, all_tiles, current_step):
                    self._cells[r][c] = next_state
                    to_remove.add((r, c))
                    (self._on_even_cells if next_state == CellState.ON_EVEN else self._on_odd_cells).add((r, c))
            self._off_cells.difference_update(to_remove)

        def can_replace_with_filled(self) -> TileInterface.FilledReplacementStatus:
            if len(self._off_cells) > 0:
                return TileInterface.FilledReplacementStatus.NO

            yes_even = True
            yes_odd = True
            for r, row in enumerate(self._cells):
                for c, cell in enumerate(row):
                    if cell == (CellState.ON_ODD if (r+c) % 2 == 0 else CellState.ON_EVEN):
                        yes_even = False
                    elif cell == (CellState.ON_EVEN if (r+c) % 2 == 0 else CellState.ON_ODD):
                        yes_odd = False

            assert yes_even != yes_odd
            return TileInterface.FilledReplacementStatus.YES_EVEN if yes_even \
                else TileInterface.FilledReplacementStatus.YES_ODD

    class FilledTile(TileInterface):
        """A tile where all non-blocked cells are on or off in a strict checkerboard pattern. All cells alternate
        between on and off, and are the opposite state of their immediate neighbours."""

        def __init__(self, cells: list[list[CellState]]):
            """Assumes this tile is being created at step_number == 0."""
            super().__init__(cells)
            assert all([cell != CellState.OFF
                        for r, row in enumerate(self._cells)
                        for c, cell in enumerate(row)])

        def cell_on(self, row: int, col: int, current_step: int) -> bool:
            required_state = CellState.ON_EVEN if current_step % 2 == 0 else CellState.ON_ODD
            return self._cells[row][col] == required_state

        def adjacent_tiles_required(self, current_step: int) -> list[tuple[int, int]]:
            # By the time a tile has been completely filled, all adjacent tiles should already have been instantiated.
            return []

        def on_cell_count(self, current_step: int) -> int:
            required_state = CellState.ON_EVEN if current_step % 2 == 0 else CellState.ON_ODD
            return len([None for row in self._cells for cell in row if cell == required_state])

        def advance(self, all_tiles: dict[tuple[int, int], TileInterface], current_step: int) -> None:
            pass

        def can_replace_with_filled(self) -> TileInterface.FilledReplacementStatus:
            return TileInterface.FilledReplacementStatus.NO

    def is_easy_solve() -> bool:
        """For this puzzle to be easily solvable for large step counts, the input must be a square of an odd width and
        height, with 'S' centred directly in the middle, a perimeter of "." around the edges, and direct paths of "."
        from S out to each edge. We also rely on puzzle_step_count % tile_width == tile_width / 2 - 0.5, as this
        ensures the points of the diamond of resulting ON tiles will lie on the edges of their tiles, and all tiles will
        be one of:
        * Completely filled
        * Half filled, approximately along a diagonal
        * Three-quarter filled, with only two adjacent corners unfilled"""
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
        if steps % tile_width != tile_width // 2 or tile_width % 2 != 1:
            return False
        return True

    def easy_solve() -> int:
        pass  # TODO

    def naive_solve() -> int:
        start_tile_cells = [[{".": CellState.OFF, "S": CellState.OFF, "#": CellState.BLOCKED}[cell] for cell in row]
                            for row in input_data]
        tiles: dict[tuple[int, int], TileInterface] = \
            {(0, 0): Tile(0, 0, [[{".": CellState.OFF, "S": CellState.ON_EVEN, "#": CellState.BLOCKED}[cell]
                                  for cell in row]
                                 for row in input_data])}
        filled_tile_even = FilledTile([[CellState.BLOCKED if cell == CellState.BLOCKED else
                                        (CellState.ON_EVEN if (r+c) % 2 == 0 else CellState.ON_ODD)
                                        for c, cell in enumerate(row)]
                                       for r, row in enumerate(start_tile_cells)])
        filled_tile_odd = FilledTile([[CellState.BLOCKED if cell == CellState.BLOCKED else
                                      (CellState.ON_EVEN if (r + c) % 2 == 1 else CellState.ON_ODD)
                                      for c, cell in enumerate(row)]
                                     for r, row in enumerate(start_tile_cells)])

        for step_number in range(steps):
            # For each tile, if cells at edges are on and no tile is adjacent, create the adjacent tile.
            new_tiles = set()
            for (tr, tc), tile in tiles.items():
                for dr, dc in tile.adjacent_tiles_required(step_number):
                    if (tr+dr, tc+dc) not in tiles:
                        new_tiles.add((tr+dr, tc+dc))
            for tr, tc in new_tiles:
                tiles[(tr, tc)] = Tile(tr, tc, copy.deepcopy(start_tile_cells))

            for tile in tiles.values():
                tile.advance(tiles, step_number)

            for tile_pos, tile in tiles.items():
                replace_status = tile.can_replace_with_filled()
                if replace_status == TileInterface.FilledReplacementStatus.YES_EVEN:
                    tiles[tile_pos] = filled_tile_even
                elif replace_status == TileInterface.FilledReplacementStatus.YES_ODD:
                    tiles[tile_pos] = filled_tile_odd

        return sum([tile.on_cell_count(steps) for tile in tiles.values()])

    if is_easy_solve():
        return easy_solve()
    else:
        return naive_solve()
