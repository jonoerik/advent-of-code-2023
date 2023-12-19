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
InputType = tuple[dict[int, Workflow], list[MachinePart]]
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
    pass  #TODO
