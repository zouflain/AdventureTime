from  __future__ import annotations
import numpy as np


class GraphNode:
    def __init__(self, parent: Graph, node_id: int, **kwargs):
        self.nid = node_id
        self.parent = parent

    def getAdjacent(self) -> list[GraphNode]:
        return self.parent.getAdjacentNodes(self.nid)


class GraphEdge:
    def __init__(self, nodes: tuple[int, int], *args, **kwargs):
        self.nodes = nodes


class Graph:
    def __init__(self):
        self.nodes = {}
        self.edges = {}
        self.next_node = 0

    def __str__(self):
        return f"""Graph {{\n\tNodes {[node.nid for node in self.nodes.values()]},\n\tEdges {[key for key in self.edges]}\n}}"""

    def addNode(self, node_type: type, **kwargs) -> int:
        node = node_type(self, self.next_node, **kwargs)
        self.nodes[self.next_node] = node
        self.next_node += 1
        return node.nid

    def addEdge(self, nodes: tuple[int, int], edge_type: type, **kwargs) -> GraphEdge:
        which = (np.min(nodes), np.max(nodes))
        edge = self.getEdge(which)
        if not edge and which[0] in self.nodes and which[1] in self.nodes:
            edge = edge_type(nodes, **kwargs)
            self.edges[which] = edge
        return edge

    def getNode(self, nid: int):
        return self.nodes.get(nid, None)

    def getEdge(self, nodes: tuple[int, int]):
        return self.edges.get(nodes, None)

    def getAdjacentNodes(self, nid: int) -> list[GraphNode]:
        adjacent = []
        for edge in self.edges.items():
            if nid in edge.nodes:
                for other in edge.nodes:
                    if nid != other:
                        adjacent.append(other)
        return [self.getNode(node) for node in adjacent]
