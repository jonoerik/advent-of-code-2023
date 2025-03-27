#!/usr/bin/env python3

from pathlib import Path
import re
from typing import Self


InputType = dict[str, set[str]]
ResultType = int


def load(input_path: Path) -> InputType:
    line_regex = re.compile(r"^(\w{3}): (\w{3}(?: \w{3})*)$")
    with open(input_path) as f:
        return {match.group(1): set(match.group(2).split())
                for match in [line_regex.fullmatch(line.strip()) for line in f.readlines()]}


def part1(input_data: InputType) -> ResultType:
    # Use a modified version of the Stoer-Wagner minimum cut algorithm, with initial edge weights of 1, to find
    # a cut of 3 edges.

    # Node names are a set of strings; the names of the nodes that were combined to form this node.
    NodeName = frozenset[str]
    NodeSet = frozenset[NodeName]
    NodePair = frozenset[NodeName]
    # Edges, stored as a dictionary of node pairs, to the weight of that edge. Node pairs stored as a set to
    # reinforce that the edge is undirected.
    EdgeSet = dict[NodePair, int]

    class Graph:
        """Undirected weighted graph."""
        def __init__(self, nodes: NodeSet, edges: EdgeSet):
            self.nodes = nodes
            self.edges = edges

        def with_merged_nodes(self, a: NodeName, b: NodeName) -> Self:
            """Return a copy of this graph, but with nodes a and b merged."""
            return Graph(frozenset({n for n in self.nodes if n != a and n != b} | {a | b}),
                         {ns: self.edges[ns] for ns in self.edges.keys() if a not in ns and b not in ns} |
                         {frozenset({a | b, n}): self.edges.get(frozenset({a, n}), 0) +
                                                 self.edges.get(frozenset({b, n}), 0) for n in self.nodes
                          if n != a and n != b and (frozenset({a, n}) in self.edges.keys() or
                                                    frozenset({b, n}) in self.edges.keys())})
                         # Edge {a, b} is dropped.

        def node_connectivity(self, n: NodeName) -> int:
            """Return the sum of all edge weights between n and the rest of the graph."""
            if len(self.nodes) <= 1:
                return 0
            return sum([self.edges.get(frozenset({n, n2}), 0) for n2 in self.nodes if n2 != n])

        def most_tightly_connected(self, ns: NodeSet) -> NodeName:
            """Return the node in this graph that is most tightly connected to the set ns, without being in ns."""
            assert len(self.nodes) > len(ns)
            connectivities = {n: sum([self.edges.get(frozenset({n, n2}), 0) for n2 in ns])
                              for n in self.nodes if n not in ns}
            return max(connectivities, key=connectivities.get)

    g = Graph(frozenset({frozenset({n}) for n in
                         set(input_data.keys()) | {n for ns in input_data.values() for n in ns}}),
              {frozenset({frozenset({n1}), frozenset({n2})}): 1
               for n1 in input_data.keys() for n2 in input_data[n1]})

    def min_cut_phase(start: NodeName) -> tuple[int, NodeName, NodeName]:
        """Returns the total weight of this 'cut of the phase', the last node (cut of the phase is between this node and
        all the other nodes), and the second-last node."""
        assert len(g.nodes) >= 2
        assert start in g.nodes
        if len(g.nodes) == 2:
            return g.node_connectivity(start), [n for n in g.nodes if n != start][0], start

        current_set: NodeSet = frozenset({start})
        last_added_node = None
        second_last_added_node = None
        cut_weight = None
        while current_set != g.nodes:
            second_last_added_node = last_added_node
            last_added_node = g.most_tightly_connected(current_set)
            cut_weight = g.node_connectivity(last_added_node)
            current_set |= {last_added_node}
        return cut_weight, last_added_node, second_last_added_node

    # Get an arbitrary node.
    a = next(iter(g.nodes))
    while len(g.nodes) > 2:
        cut_size, n1, n2 = min_cut_phase(a)
        if cut_size == 3:
            return len(n1) * sum([len(n) for n in g.nodes if n != n1])
        g = g.with_merged_nodes(n1, n2)

    # Should have found a suitable cut.
    assert False


def part2(input_data: InputType) -> ResultType:
    pass  # TODO
