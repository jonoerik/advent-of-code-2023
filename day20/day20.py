#!/usr/bin/env python3

from enum import IntEnum
from pathlib import Path
import re


class ModuleType(IntEnum):
    BROADCAST = 0
    FLIPFLOP = 1
    CONJUNCTION = 2
    OUTPUT = 3


# Dict from module name to (module type, list of destination modules)
InputType = dict[str, tuple[ModuleType, list[str]]]
ResultType = int


def load(input_path: Path) -> InputType:
    line_regex = re.compile(r"^(?P<type>[%&]?)(?P<name>\w+) -> (?P<destinations>[\w, ]+)$")
    with open(input_path) as f:
        return {match["name"]: (ModuleType.BROADCAST if match["name"] == "broadcaster" else
                                ModuleType.FLIPFLOP if match["type"] == "%" else
                                ModuleType.CONJUNCTION if match["type"] == "&" else
                                ModuleType.OUTPUT,
                                match["destinations"].split(", "))
                for match in [line_regex.fullmatch(line.strip()) for line in f.readlines()]}


def part1(input_data: InputType) -> ResultType:
    high_signals = 0
    low_signals = 0
    flip_flop_states = {module: False for module, (module_type, _) in input_data.items()
                        if module_type == ModuleType.FLIPFLOP}
    conjunction_states = {module: {source_module: False for source_module, (_, source_module_destinations)
                                   in input_data.items() if module in source_module_destinations}
                          for module, (module_type, _) in input_data.items() if module_type == ModuleType.CONJUNCTION}
    input_data.update({module: (ModuleType.OUTPUT, []) for module in
                       {module for _, dests in input_data.values() for module in dests} if module not in input_data})

    for _ in range(1000):
        # Signals that have yet to be delivered, earliest sent first.
        # Signals are (destination, source (or None for the button), is_high)
        pending_signals: list[tuple[str, str | None, bool]] = [("broadcaster", None, False)]

        while pending_signals:
            current_dest, current_source, current_is_high = pending_signals.pop()
            if current_is_high:
                high_signals += 1
            else:
                low_signals += 1

            match input_data[current_dest]:
                case ModuleType.BROADCAST, next_dests:
                    pending_signals.extend([(next_dest, current_dest, current_is_high) for next_dest in next_dests])
                case ModuleType.FLIPFLOP, next_dests:
                    if not current_is_high:
                        flip_flop_states[current_dest] = not flip_flop_states[current_dest]
                        pending_signals.extend([(next_dest, current_dest, flip_flop_states[current_dest])
                                                for next_dest in next_dests])
                case ModuleType.CONJUNCTION, next_dests:
                    conjunction_states[current_dest][current_source] = current_is_high
                    pending_signals.extend([(next_dest, current_dest,
                                             not all(conjunction_states[current_dest].values()))
                                            for next_dest in next_dests])
                case ModuleType.OUTPUT, _:
                    pass

    return high_signals * low_signals


def part2(input_data: InputType) -> ResultType:
    pass  #TODO
