#!/usr/bin/env python3

from pathlib import Path
import re
import typing


class MachinePart(typing.NamedTuple):
    x: int
    m: int
    a: int
    s: int


Workflow = list[tuple[str, str, int, str] | str]
InputType = tuple[dict[str, Workflow], list[MachinePart]]
ResultType = int

workflow_regex = re.compile(r"^(?P<name>[a-z]+)\{(?P<rules>[^}]+),(?P<unconditional_rule>\w+)}$")
workflow_rule_regex = re.compile(r"^([xmas])([<>])(\d+):(\w+)$")
machine_part_regex = re.compile(r"^\{x=(?P<x>\d+),m=(?P<m>\d+),a=(?P<a>\d+),s=(?P<s>\d+)}$")


def load(input_path: Path) -> InputType:
    workflows = {}
    parts = []

    with open(input_path) as f:
        while line := f.readline():
            line = line.strip()
            if not line:
                break

            match = workflow_regex.fullmatch(line)
            rules = []

            for rule_part in match.group("rules").split(","):
                rule_match = workflow_rule_regex.fullmatch(rule_part)
                rules.append((rule_match.group(1), rule_match.group(2), int(rule_match.group(3)), rule_match.group(4)))
            rules.append(match.group("unconditional_rule"))

            workflows[match.group("name")] = rules

        while line := f.readline():
            line = line.strip()
            match = machine_part_regex.fullmatch(line)
            parts.append(MachinePart(x=int(match.group("x")), m=int(match.group("m")),
                                     a=int(match.group("a")), s=int(match.group("s"))))

    return workflows, parts


def part1(input_data: InputType) -> ResultType:
    workflows, parts = input_data

    def part_accepted(part: MachinePart) -> bool:
        current_workflow = "in"
        while True:
            for current_rule in workflows[current_workflow]:
                match current_rule:
                    case member, "<", v, target_workflow:
                        if getattr(part, member) < v:
                            current_workflow = target_workflow
                            break
                    case member, ">", v, target_workflow:
                        if getattr(part, member) > v:
                            current_workflow = target_workflow
                            break
                    case target_workflow:
                        current_workflow = target_workflow
                        break
            if current_workflow == "A":
                return True
            elif current_workflow == "R":
                return False

    return sum([sum(part) for part in parts if part_accepted(part)])


def part2(input_data: InputType) -> ResultType:
    workflows, _ = input_data

    class MachinePartRange(typing.NamedTuple):
        """Ranges are inclusive of both lower and upper bound."""
        x: tuple[int, int]
        m: tuple[int, int]
        a: tuple[int, int]
        s: tuple[int, int]

    def range_split(part_range: MachinePartRange, member: str, v: int,
                    comparison: typing.Callable[[int, int], bool],
                    make_new_range: typing.Callable[[tuple[int, int], int], tuple[int, int]]
                    ) -> MachinePartRange | None:
        member_range = getattr(part_range, member)
        if all([comparison(x, v) for x in member_range]):
            return part_range
        if not any([comparison(x, v) for x in member_range]):
            return None
        # Quick hack to return MachinePartRange with a single member modified.
        return MachinePartRange(**{m: make_new_range(member_range, v) if m == member else n
                                   for m, n in part_range._asdict().items()})

    def accepted_ranges(part_range: MachinePartRange, workflow: str, rule_index: int) -> list[MachinePartRange]:
        match workflows[workflow][rule_index]:
            case member, "<", v, target_workflow:
                result = []
                if mpr := range_split(part_range, member, v, lambda a, b: a < b, lambda a, b: (a[0], b-1)):
                    if target_workflow == "A":
                        result.append(mpr)
                    elif target_workflow != "R":
                        result.extend(accepted_ranges(mpr, target_workflow, 0))
                if mpr := range_split(part_range, member, v, lambda a, b: a >= b, lambda a, b: (b, a[1])):
                    result.extend(accepted_ranges(mpr, workflow, rule_index+1))
                return result
            case member, ">", v, target_workflow:
                result = []
                if mpr := range_split(part_range, member, v, lambda a, b: a > b, lambda a, b: (b + 1, a[1])):
                    if target_workflow == "A":
                        result.append(mpr)
                    elif target_workflow != "R":
                        result.extend(accepted_ranges(mpr, target_workflow, 0))
                if mpr := range_split(part_range, member, v, lambda a, b: a <= b, lambda a, b: (a[0], b)):
                    result.extend(accepted_ranges(mpr, workflow, rule_index + 1))
                return result
            case "A":
                return [part_range]
            case "R":
                return []
            case target_workflow:
                return accepted_ranges(part_range, target_workflow, 0)

    return sum([(ar.x[1] - ar.x[0] + 1) * (ar.m[1] - ar.m[0] + 1) * (ar.a[1] - ar.a[0] + 1) * (ar.s[1] - ar.s[0] + 1)
                for ar in accepted_ranges(MachinePartRange((1, 4000), (1, 4000), (1, 4000), (1, 4000)), "in", 0)])
