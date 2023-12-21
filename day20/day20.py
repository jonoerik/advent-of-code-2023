#!/usr/bin/env python3

import collections
from enum import IntEnum
import itertools
import math
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

FlipFlopStatesType = dict[str, bool]
ConjunctionStatesType = dict[str, dict[str, bool]]
# A single signal as (destination, source (or None for the button), is_high).
SignalType = tuple[str, str | None, bool]


def load(input_path: Path) -> InputType:
    line_regex = re.compile(r"^(?P<type>[%&]?)(?P<name>\w+) -> (?P<destinations>[\w, ]+)$")
    with open(input_path) as f:
        return {match["name"]: (ModuleType.BROADCAST if match["name"] == "broadcaster" else
                                ModuleType.FLIPFLOP if match["type"] == "%" else
                                ModuleType.CONJUNCTION if match["type"] == "&" else
                                ModuleType.OUTPUT,
                                match["destinations"].split(", "))
                for match in [line_regex.fullmatch(line.strip()) for line in f.readlines()]}


def start_states(input_data: InputType) -> tuple[FlipFlopStatesType, ConjunctionStatesType]:
    flip_flop_states = {module: False for module, (module_type, _) in input_data.items()
                        if module_type == ModuleType.FLIPFLOP}
    conjunction_states = {module: {source_module: False for source_module, (_, source_module_destinations)
                                   in input_data.items() if module in source_module_destinations}
                          for module, (module_type, _) in input_data.items() if module_type == ModuleType.CONJUNCTION}
    return flip_flop_states, conjunction_states


def handle_signal(input_data: InputType,
                  flip_flop_states: FlipFlopStatesType, conjunction_states: ConjunctionStatesType,
                  signal: SignalType) -> list[SignalType]:
    current_dest, current_source, current_is_high = signal

    match input_data[current_dest]:
        case ModuleType.BROADCAST, next_dests:
            return [(next_dest, current_dest, current_is_high) for next_dest in next_dests]
        case ModuleType.FLIPFLOP, next_dests:
            if not current_is_high:
                flip_flop_states[current_dest] = not flip_flop_states[current_dest]
                return [(next_dest, current_dest, flip_flop_states[current_dest])
                        for next_dest in next_dests]
        case ModuleType.CONJUNCTION, next_dests:
            conjunction_states[current_dest][current_source] = current_is_high
            return[(next_dest, current_dest,
                    not all(conjunction_states[current_dest].values()))
                   for next_dest in next_dests]
        case ModuleType.OUTPUT, _:
            pass

    return []


def part1(input_data: InputType) -> ResultType:
    high_signals = 0
    low_signals = 0
    input_data.update({module: (ModuleType.OUTPUT, []) for module in
                       {module for _, dests in input_data.values() for module in dests} if module not in input_data})
    flip_flop_states, conjunction_states = start_states(input_data)

    for _ in range(1000):
        # Signals that have yet to be delivered, earliest sent first.
        pending_signals = collections.deque([("broadcaster", None, False)])
        while pending_signals:
            current_signal = pending_signals.popleft()
            if current_signal[2]:
                high_signals += 1
            else:
                low_signals += 1
            pending_signals.extend(handle_signal(input_data, flip_flop_states, conjunction_states, current_signal))

    return high_signals * low_signals


def part2(input_data: InputType) -> ResultType:
    input_data.update({module: (ModuleType.OUTPUT, []) for module in
                      {module for _, dests in input_data.values() for module in dests} if module not in input_data})
    flip_flop_states, conjunction_states = start_states(input_data)

    def print_dot_diagram() -> None:
        """Output the contents of a TikZ dot file of the signal connection graph.
        Helpful for visually identifying patterns in the input."""
        print("strict digraph {")
        for a, t in [(a, t) for a, (t, _) in input_data.items()]:
            shape = {ModuleType.BROADCAST: 'invhouse', ModuleType.FLIPFLOP: 'diamond',
                     ModuleType.CONJUNCTION: 'invtrapezium', ModuleType.OUTPUT: 'box'}[t]
            colour = {ModuleType.BROADCAST: 'white', ModuleType.FLIPFLOP: 'palegreen',
                      ModuleType.CONJUNCTION: 'orange', ModuleType.OUTPUT: 'white'}[t]
            print(f"    {a} [shape={shape} fillcolor={colour} style=filled]")
        for a, b in [(a, b) for a, (_, dests) in input_data.items() for b in dests]:
            print(f"    {a} -> {b}")
        print("}")

    def get_graph_magic_numbers() -> None | list[int]:
        """Identify if this graph is of a shape that we know how to solve easily.
        Shape is:
            broadcaster -> n different chains
            Each chain is flip-flops, the output of one feeding into the next:
                Each chain has a single conjunction, which feeds in from some of the chain flip-flops, and out to
                others.
                The first flip-flop in the chain has a connection from the broadcaster and the conjunction, and out to
                the conjunction again.
                Other chain flip-flops have exactly one connection either to or from the conjunction.
                The last flip-flop in the chain has a connection out to the conjunction.
            Each chain's conjunction feeds through an inverter conjunction, and all into a merge conjunction.
            This merge conjunction feeds into rx.
        If the graph doesn't match this expected shape, return None.
        Otherwise, return the 'magic number' for each chain; a number which in binary has the same length as
        the flip-flop chain, and has 1s for the flip-flops which feed into the conjunction. Note that the lowest bit
        is the flip-flop fed from the broadcaster, and the highest bit is always 1 as that flip-flop always feeds
        back to the conjunction.
        Each button-press increments the integer represented by each flip-flop chain by 1. A chain's conjunction first
        outputs low when the flip-flop chain is set to that chain's magic number. After this happens, the flip-flops are
        immediately set back to low, starting the cycle again."""
        # Module name -> (type, sources, destinations).
        modules = {module: (t, sorted([source_module for source_module, (_, source_module_destinations)
                                       in input_data.items() if module in source_module_destinations]), sorted(dests))
                   for (module, (t, dests)) in input_data.items()}

        try:
            final_conjunction = modules["rx"][1][0]

            def get_ff_chain(start: str) -> tuple[list[tuple[str, bool]], str, str]:
                chain = [(start, True)]
                while True:
                    chain_conjunction = [module for module in modules[start][2]
                                         if modules[module][0] == ModuleType.CONJUNCTION][0]
                    chain_inverter = [module for module in modules[chain_conjunction][2]
                                      if modules[module][0] == ModuleType.CONJUNCTION][0]
                    next_modules = [module for module in modules[chain[-1][0]][2]
                                    if modules[module][0] == ModuleType.FLIPFLOP]
                    if not next_modules:
                        break
                    chain.append((next_modules[0], next_modules[0] in modules[chain_conjunction][1]))
                return chain, chain_conjunction, chain_inverter

            # List of (ordered list of (flip-flop, feeds into conjunction?)), conjunction, inverter after conjunction).
            chains = list(map(get_ff_chain, modules["broadcaster"][2]))

        except (KeyError, IndexError):
            return None

        expected_modules = {"broadcaster": (ModuleType.BROADCAST, [], [ff_chain[0][0][0] for ff_chain in chains]),
                            "rx": (ModuleType.OUTPUT, [final_conjunction], []),
                            final_conjunction: (ModuleType.CONJUNCTION, [chain[2] for chain in chains], ["rx"])}
        for chain in chains:
            for i, (ff, into_conjunction) in enumerate(chain[0]):
                if i == 0:
                    srcs = ["broadcaster", chain[1]]
                    dests = [chain[0][1][0], chain[1]]
                elif i == len(chain[0]) - 1:
                    srcs = [chain[0][i-1][0]]
                    dests = [chain[1]]
                else:
                    srcs = [chain[0][i-1][0]] + ([chain[1]] if not into_conjunction else [])
                    dests = [chain[0][i+1][0]] + ([chain[1]] if into_conjunction else [])
                expected_modules |= {ff: (ModuleType.FLIPFLOP, srcs, dests)}
            expected_modules |= {chain[1]: (ModuleType.CONJUNCTION, [chain[0][0][0], chain[0][-1][0]] +
                                            [module for module, into_conjunction in chain[0][1:-1] if into_conjunction],
                                            [chain[0][0][0], chain[2]] + [module for module, into_conjunction in
                                                                          chain[0][1:-1] if not into_conjunction])}
            expected_modules |= {chain[2]: (ModuleType.CONJUNCTION, [chain[1]], [final_conjunction])}

        expected_modules = {name: (t, sorted(srcs), sorted(dests))
                            for name, (t, srcs, dests) in expected_modules.items()}

        # Note that this check won't find issues in input_data's ordering of output connections in a module
        # which may prevent it from working as expected, and lead to an incorrect answer.
        if modules != expected_modules:
            return None
        else:
            return [sum([2**i for i, x in enumerate(
                [True] + [into_conjunction for _, into_conjunction in chain[1:-1]] + [True]) if x])
                    for chain, _, _ in chains]

    magic_numbers = get_graph_magic_numbers()
    if magic_numbers is not None:
        # To reach a state where a magic-number-subgraph is outputting the signal required to set rx low,
        # the subgraph requires magic-number button presses. After this occurs, the subgraph immediately switches
        # all its flip-flops back to low, restarting the cycle.
        return math.lcm(*magic_numbers)
    else:
        # Graph doesn't have easy-to-solve shape, so fall back on manual simulation.
        for button_presses in itertools.count(1):
            # Signals that have yet to be delivered, earliest sent first.
            pending_signals = collections.deque([("broadcaster", None, False)])
            while pending_signals:
                pending_signals.extend(handle_signal(input_data, flip_flop_states, conjunction_states,
                                                     pending_signals.popleft()))
                if ("rx", False) in [(dest, is_high) for dest, _, is_high in pending_signals]:
                    return button_presses
