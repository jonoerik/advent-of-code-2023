#!/usr/bin/env python3

import collections
from enum import IntEnum
import itertools
from pathlib import Path
import re


class Direction(IntEnum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3


InputType = list[tuple[Direction, int, str]]
ResultType = int


def load(input_path: Path) -> InputType:
    line_regex = \
        re.compile(r"^(?P<dir>[URDL]) (?P<dist>\d+) \(#(?P<colour>[0-9a-f]{6})\)$")
    with open(input_path) as f:
        return [({"U": Direction.UP,
                  "R": Direction.RIGHT,
                  "D": Direction.DOWN,
                  "L": Direction.LEFT}[match.group("dir")],
                 int(match.group("dist")),
                 match.group("colour"))
                for match in map(line_regex.fullmatch, [line.strip() for line in f.readlines()])]


Point = tuple[int, int]
# Closed polygon, clockwise winding order.
Polygon = list[Point]
Line = tuple[Point, Point]


def part1(input_data: InputType) -> ResultType:
    def dig_trench() -> list[list[bool]]:
        row = 0
        col = 0
        result = [[True]]
        for direction, dist, colour in input_data:
            match direction:
                case Direction.UP:
                    dist_to_edge = min(row, dist)
                    for i in range(dist_to_edge):
                        result[row - i - 1][col] = True
                    if dist_to_edge < dist:
                        result = [[c == col for c in range(len(result[0]))]
                                  for _ in range(dist - dist_to_edge)] + result
                    row = max(0, row - dist)
                case Direction.RIGHT:
                    dist_to_edge = min(len(result[0]) - 1 - col, dist)
                    for i in range(dist_to_edge):
                        result[row][col + i + 1] = True
                    if dist_to_edge < dist:
                        result = [r + [n == row for _ in range(dist - dist_to_edge)]
                                  for n, r in enumerate(result)]
                    col += dist
                case Direction.DOWN:
                    dist_to_edge = min(len(result) - 1 - row, dist)
                    for i in range(dist_to_edge):
                        result[row + i + 1][col] = True
                    if dist_to_edge < dist:
                        result = result + [[c == col for c in range(len(result[0]))]
                                           for _ in range(dist - dist_to_edge)]
                    row += dist
                case Direction.LEFT:
                    dist_to_edge = min(col, dist)
                    for i in range(dist_to_edge):
                        result[row][col - i - 1] = True
                    if dist_to_edge < dist:
                        result = [[n == row for _ in range(dist - dist_to_edge)] + r
                                  for n, r in enumerate(result)]
                    col = max(0, col - dist)
        return result
    trench = dig_trench()

    def dig_middle() -> list[list[bool]]:
        result = [[True for _ in range(len(trench[0]))] for _ in range(len(trench))]
        # Flood fill from outer edges.
        to_visit = {(0, i) for i in range(len(trench[0]))} | {(len(trench) - 1, i) for i in range(len(trench[0]))} | \
                   {(i, 0) for i in range(len(trench))} | {(i, len(trench[0]) - 1) for i in range(len(trench))}
        while to_visit:
            visiting = to_visit.pop()
            if 0 <= visiting[0] < len(trench) and 0 <= visiting[1] < len(trench[0]) and \
                    result[visiting[0]][visiting[1]] and not trench[visiting[0]][visiting[1]]:
                result[visiting[0]][visiting[1]] = False
                to_visit.update({(visiting[0] + dr, visiting[1] + dc) for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]})
        return result
    pit = dig_middle()

    return sum([1 if cell else 0 for row in pit for cell in row])


def part2(input_data: InputType) -> ResultType:
    input_data = [({0: Direction.RIGHT, 1: Direction.DOWN, 2: Direction.LEFT, 3: Direction.UP}
                   [int(c[5])], int(c[:5], 16), c) for a, b, c in input_data]

    def dig_trenches() -> list[Polygon]:
        """From the set of trench digging instructions, produce a set of square polygons around the areas that have
        been dug out."""
        result = [[(0, 0), (0, 1), (1, 1), (1, 0)]]
        current_row = 0
        current_col = 0
        for direction, dist, _ in input_data:
            match direction:
                case Direction.UP:
                    result.append([(current_row, current_col), (current_row - dist, current_col),
                                   (current_row - dist, current_col + 1), (current_row, current_col + 1)])
                    current_row -= dist
                case Direction.RIGHT:
                    result.append([(current_row, current_col + 1), (current_row, current_col + 1 + dist),
                                   (current_row + 1, current_col + 1 + dist), (current_row + 1, current_col + 1)])
                    current_col += dist
                case Direction.DOWN:
                    result.append([(current_row + 1, current_col + 1), (current_row + 1 + dist, current_col + 1),
                                   (current_row + 1 + dist, current_col), (current_row + 1, current_col)])
                    current_row += dist
                case Direction.LEFT:
                    result.append([(current_row + 1, current_col), (current_row + 1, current_col - dist),
                                   (current_row, current_col - dist), (current_row, current_col)])
                    current_col -= dist
        return result

    def intersection(a: Line, b: Line) -> list[Point]:
        """If a intersects with or touches b, return the point of that intersection in a list, else return an empty
        list.
        If b overlaps with a (e.g. horizontal lines with the same row value), return the end points of b that are
        within a.
        The ends of a are not considered, but the ends of b are. i.e. An end of a touching the middle of b is not
        considered, but an end of b touching the middle of a is returned as an intersection."""
        # Ensure lines going down/right for convenience of next section.
        if a[0] > a[1]:
            a = (a[1], a[0])
        if b[0] > b[1]:
            b = (b[1], b[0])

        match a, b:
            case ((ra1, ca1), (ra2, ca2)), ((rb1, cb1), (rb2, cb2)) if ra1 == ra2 == rb1 == rb2:
                # 2 horizontal lines in same row.
                return [(ra1, c) for c in [cb1, cb2] if ca1 < c < ca2]
            case ((ra1, ca1), (ra2, ca2)), ((rb1, cb1), (rb2, cb2)) if ca1 == ca2 == cb1 == cb2:
                # 2 vertical lines in same column.
                return [(r, ca1) for r in [rb1, rb2] if ra1 < r < ra2]
            case ((ra1, ca1), (ra2, ca2)), ((rb1, cb1), (rb2, cb2)) if \
                    (ra1 == ra2 != rb1 == rb2) or ca1 == ca2 != cb1 == cb2:
                # 2 parallel but offset lines.
                return []
            case ((ra1, ca1), (ra2, ca2)), ((rb1, cb1), (rb2, cb2)) if ra1 == ra2 and cb1 == cb2:
                # Horizontal a, vertical b.
                return [(ra1, cb1)] if rb1 <= ra1 <= rb2 and ca1 < cb1 < ca2 else []
            case ((ra1, ca1), (ra2, ca2)), ((rb1, cb1), (rb2, cb2)) if rb1 == rb2 and ca1 == ca2:
                # Vertical a, horizontal b.
                return [(rb1, ca1)] if ra1 < rb1 < ra2 and cb1 <= ca1 <= cb2 else []
            case _:
                # All cases of horizontal/vertical lines should be captured by the previous cases.
                assert False

    def split_at_intersections(rects: list[Polygon]) -> list[Polygon]:
        """For all rectangles in rects, add additional vertices at points which touch or intersect with other edges."""
        new_rects: list[Polygon] = []
        for rect in rects:
            new_rect: Polygon = []
            for line in itertools.pairwise(rect + [rect[0]]):
                # Only copy the first point in line to the new line; the last point will be in another line segment.
                line_points: set[Point] = {line[0]}
                for other_rect in [r for r in rects if id(r) != id(rect)]:
                    for other_line in itertools.pairwise(other_rect + [other_rect[0]]):
                        line_points.update(intersection(line, other_line))
                # Reverse the points in line_points if the original line was pointing up or left, so that the new
                # line matches the direction of the original.
                new_rect.extend(list(sorted(line_points, reverse=(line[0] > line[1]))))
            new_rects.append(new_rect)
        return new_rects

    def find_outline(polys: list[Polygon]) -> Polygon:
        """Implement algorithm from answer by Joseph O'Rourke on stack exchange question "How do I combine complex
        polygons?" by user grenade.
        https://stackoverflow.com/questions/2667748/how-do-i-combine-complex-polygons/19475433#19475433
        This implementation assumes all input polygons are touching, and all lines are vertical or horizontal."""
        # Choose the left-most of the highest points to start with.
        start_point = min([point for poly in polys for point in poly])

        edges: collections.defaultdict[Point, set[Point]] = collections.defaultdict(set)
        for poly in polys:
            for a, b in itertools.pairwise(poly + [poly[0]]):
                edges[a].add(b)
                edges[b].add(a)

        outline = []
        current_point = start_point
        # As start_point is in the upper-left, we can assume a line comes into it from below.
        last_direction = Direction.UP

        def find_next_point() -> tuple[Point, Direction]:
            for next_direction in [Direction((last_direction - 1 + i) % len(Direction)) for i in range(3)]:
                candidates = []
                match next_direction:
                    case Direction.UP:
                        candidates = [(r, c) for r, c in edges[current_point] if
                                      r < current_point[0] and c == current_point[1]]
                    case Direction.RIGHT:
                        candidates = [(r, c) for r, c in edges[current_point] if
                                      r == current_point[0] and c > current_point[1]]
                    case Direction.DOWN:
                        candidates = [(r, c) for r, c in edges[current_point] if
                                      r > current_point[0] and c == current_point[1]]
                    case Direction.LEFT:
                        candidates = [(r, c) for r, c in edges[current_point] if
                                      r == current_point[0] and c < current_point[1]]
                if candidates:
                    return (max if next_direction == Direction.UP or next_direction == Direction.LEFT else min)(
                        candidates), next_direction
            assert False

        while True:
            # Proceed clockwise around the outline polygon.
            outline.append(current_point)
            # Merge last 3 elements into 2 if they lie on a straight line.
            match outline:
                case *_, (r1, c1), (r2, c2), (r3, c3) if r1 == r2 == r3 or c1 == c2 == c3:
                    outline[-2:] = [(r3, c3)]

            current_point, last_direction = find_next_point()
            if current_point == start_point:
                break

        # Merge last 2 elements if they lie on a straight line with the starting point.
        match outline:
            case (r1, c1), *_, (r2, c2), (r3, c3) if r1 == r2 == r3 or c1 == c2 == c3:
                outline[-2:] = [(r2, c2)]
        return outline

    def calculate_area(poly: Polygon) -> int:
        """My own algorithm (though likely already described elsewhere) for finding the area within a rectilinear
        polygon."""
        # Find column coordinates where a line either begins or ends.
        # Between adjacent column_ends, the polygon exists as bands; sets of rectangles between one column and the
        # other. Additionally, the polygon is bounded by the outermost column_ends.
        column_ends = sorted(set([c for _, c in poly]))

        def intersecting_horizontals(c1: int, c2: int) -> set[int]:
            """Find all horizontal lines from poly which cross the space between columns c1 and c2."""
            return {ra for ((ra, ca), (rb, cb)) in itertools.pairwise(poly + [poly[0]]) if
                    ra == rb and min(ca, cb) <= min(c1, c2) and max(ca, cb) >= max(c1, c2)}

        result = 0
        for start_col, end_col in itertools.pairwise(column_ends):
            horizontals = sorted(intersecting_horizontals(start_col, end_col))
            # Within each column, there should be an even number of crossing horizontal lines.
            assert len(horizontals) % 2 == 0
            # For 2n lines crossing this column, there must be n rectangular areas inside the polygon.
            # Areas between the horizontal lines alternate in/out of the polygon.
            for start_row, end_row in zip(horizontals[::2], horizontals[1::2]):
                result += abs(end_col - start_col) * abs(end_row - start_row)

        return result

    return calculate_area(find_outline(split_at_intersections(dig_trenches())))
