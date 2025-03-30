#!/usr/bin/env python3

import collections
import copy
from pathlib import Path
import re

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
    # Edges, stored as a dictionary of start node, to dictionary of end node to weight.
    # Each edge should appear twice; once for each direction.
    EdgeSet = dict[NodeName, dict[NodeName, int]]

    class Graph:
        """Undirected weighted graph."""
        def __init__(self, edges: EdgeSet):
            # self.keys() is the set of vertices.
            self.edges: EdgeSet = edges

        def merge_nodes(self, a: NodeName, b: NodeName):
            a_edges = copy.deepcopy(self.edges[a])
            b_edges = copy.deepcopy(self.edges[b])
            new_edges = {n: a_edges.get(n, 0) + b_edges.get(n, 0) for n in set(a_edges.keys()) | set(b_edges.keys()) if n != a and n != b}
            merged_node_name = frozenset(a | b)

            self.edges.pop(a)
            self.edges.pop(b)
            for n in a_edges:
                if n != b:
                    self.edges[n].pop(a)
            for n in b_edges:
                if n != a:
                    self.edges[n].pop(b)

            self.edges[merged_node_name] = new_edges
            for n, w in new_edges.items():
                self.edges[n][merged_node_name] = w

        def node_connectivity(self, n: NodeName) -> int:
            """Return the sum of all edge weights between n and the rest of the graph."""
            if len(self.edges) <= 1:
                return 0
            return sum(self.edges[n].values())

        def most_tightly_connected(self, ns: NodeSet) -> NodeName:
            """Return the node in this graph that is most tightly connected to the set ns, without being in ns."""
            assert len(self.edges) > len(ns)

            # Scan the smaller set of ns, nodes-ns.
            if len(ns) <= len(self.edges) // 2:
                connectivities = collections.defaultdict(lambda: 0)
                for n in ns:
                    for n2 in self.edges[n]:
                        if n2 not in ns:
                            connectivities[n2] += self.edges[n][n2]
            else:
                connectivities = collections.defaultdict(lambda: 0)
                for n in [n for n in self.edges.keys() if n not in ns]:
                    for n2 in self.edges[n]:
                        if n2 in ns:
                            connectivities[n] += self.edges[n][n2]

            return max(connectivities, key=connectivities.get)

    edges = {}
    for n1, ns in input_data.items():
        for n2 in ns:
            if frozenset({n1}) not in edges:
                edges[frozenset({n1})] = {}
            if frozenset({n2}) not in edges:
                edges[frozenset({n2})] = {}
            edges[frozenset({n1})][frozenset({n2})] = 1
            edges[frozenset({n2})][frozenset({n1})] = 1
    g = Graph(edges)

    def min_cut_phase(start: NodeName) -> tuple[int, NodeName, NodeName]:
        """Returns the total weight of this 'cut of the phase', the last node (cut of the phase is between this node and
        all the other nodes), and the second-last node."""
        assert len(g.edges.keys()) >= 2
        assert start in g.edges.keys()
        if len(g.edges.keys()) == 2:
            return g.node_connectivity(start), [n for n in g.edges.keys() if n != start][0], start

        current_set: NodeSet = frozenset({start})
        last_added_node = None
        second_last_added_node = None
        cut_weight = None
        while current_set != g.edges.keys():
            second_last_added_node = last_added_node
            last_added_node = g.most_tightly_connected(current_set)
            cut_weight = g.node_connectivity(last_added_node)
            current_set |= {last_added_node}
        return cut_weight, last_added_node, second_last_added_node

    # Get an arbitrary node.
    a = next(iter(g.edges.keys()))
    while len(g.edges.keys()) > 2:
        cut_size, n1, n2 = min_cut_phase(a)
        if cut_size == 3:
            return len(n1) * sum([len(n) for n in g.edges.keys() if n != n1])
        g.merge_nodes(n1, n2)

        while True:
            # Merge all node pairs that have an edge of weight greater than 3 between them, as the 3-cut can never
            # be between these nodes.
            mergeable_nodes = [(n1, n2) for n1 in g.edges.keys() for n2 in g.edges[n1].keys() if g.edges[n1][n2] > 3]
            if mergeable_nodes:
                g.merge_nodes(mergeable_nodes[0][0], mergeable_nodes[0][1])
            else:
                break

    # Should have found a suitable cut.
    assert False
