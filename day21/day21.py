#!/usr/bin/env python3

import copy
from enum import IntEnum
from pathlib import Path

InputType = list[str]
ResultType = int


def load(input_path: Path) -> InputType:
    with open(input_path) as f:
        return [line.strip() for line in f.readlines()]


class TileState(IntEnum):
    OFF = 0
    ON = 1
    BLOCKED = 2


def part1(input_data: InputType, steps: int = 64) -> ResultType:
    input_data = [[{".": TileState.OFF, "S": TileState.ON, "#": TileState.BLOCKED}[cell] for cell in row]
                  for row in input_data]

    def on_in_neighbourhood(r: int, c: int) -> bool:
        for nr, nc in [(r + dr, c + dc) for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]
                       if 0 <= r + dr < len(input_data) and 0 <= c + dc < len(input_data[0])]:
            if input_data[nr][nc] == TileState.ON:
                return True
        return False

    for _ in range(steps):
        input_data = [[cell if cell == TileState.BLOCKED else
                       (TileState.ON if on_in_neighbourhood(row_index, col_index) else TileState.OFF)
                       for col_index, cell in enumerate(row)] for row_index, row in enumerate(input_data)]

    return sum([row.count(TileState.ON) for row in input_data])


def part2(input_data: InputType, steps: int = 26501365) -> ResultType:
    def is_easy_solve() -> bool:
        """For this puzzle to be easily solvable for large step counts, the input must be a square of an odd width and
        height, with 'S' centred directly in the middle, a perimeter of "." around the edges, and direct paths of "."
        from S out to each edge."""
        if len(input_data) != len(input_data[0]):
            return False
        if len(input_data) % 2 != 1 or len(input_data[0]) % 2 != 1:
            return False
        for row in [0, len(input_data) // 2, len(input_data) - 1]:
            if "#" in input_data[row]:
                return False
        for col in [0, len(input_data[0]) // 2, len(input_data[0]) - 1]:
            if "#" in [row[col] for row in input_data]:
                return False
        if input_data[len(input_data) // 2][len(input_data[0]) // 2] != "S":
            return False
        return True

    def easy_solve() -> int:
        pass #TODO

    def naive_solve() -> int:
        start_tile = [[{".": TileState.OFF, "S": TileState.OFF, "#": TileState.BLOCKED}[cell] for cell in row]
                      for row in input_data]
        tile_height = len(start_tile)
        tile_width = len(start_tile[0])
        tiles: dict[tuple[int, int], list[list[TileState]]] = \
            {(0, 0): [[{".": TileState.OFF, "S": TileState.ON, "#": TileState.BLOCKED}[cell] for cell in row]
                      for row in input_data]}

        def on_in_neighbourhood(tile_r: int, tile_c: int, r: int, c: int) -> bool:
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr = r + dr
                nc = c + dc
                tr = tile_r
                tc = tile_c
                if nr == -1:
                    tr -= 1
                    nr = tile_height - 1
                if nr == tile_height:
                    tr += 1
                    nr = 0
                if nc == -1:
                    tc -= 1
                    nc = tile_width - 1
                if nc == tile_width:
                    tc += 1
                    nc = 0
                if (tr, tc) in tiles:
                    if tiles[(tr, tc)][nr][nc] == TileState.ON:
                        return True
            return False

        for _ in range(steps):
            # For each tile, if cells at edges are on and no tile is adjacent, create the adjacent tile.
            new_tiles = []
            for tr, tc in tiles.keys():
                if (tr-1, tc) not in tiles:
                    if TileState.ON in tiles[(tr, tc)][0]:
                        new_tiles.append((tr-1, tc))
                if (tr+1, tc) not in tiles:
                    if TileState.ON in tiles[(tr, tc)][tile_height-1]:
                        new_tiles.append((tr+1, tc))
                if (tr, tc-1) not in tiles:
                    if TileState.ON in [row[0] for row in tiles[(tr, tc)]]:
                        new_tiles.append((tr, tc-1))
                if (tr, tc+1) not in tiles:
                    if TileState.ON in [row[tile_width-1] for row in tiles[(tr, tc)]]:
                        new_tiles.append((tr, tc+1))
            for new_tile in new_tiles:
                tiles[new_tile] = copy.deepcopy(start_tile)

            # Update tiles.
            tiles = {(tr, tc): [[TileState.BLOCKED if cell == TileState.BLOCKED else
                                 (TileState.ON if on_in_neighbourhood(tr, tc, r, c) else TileState.OFF)
                                 for c, cell in enumerate(row)]
                                for r, row in enumerate(tile)]
                     for (tr, tc), tile in tiles.items()}

        return sum([sum([row.count(TileState.ON) for row in tile]) for tile in tiles.values()])

    if is_easy_solve():
        return easy_solve()
    else:
        return naive_solve()
