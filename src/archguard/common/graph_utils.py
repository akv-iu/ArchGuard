"""Utility functions for working with NetworkX graphs in ArchGuard."""

from typing import Dict, List, Optional, Set, Tuple

import networkx as nx


def find_path(
    graph: nx.DiGraph, source: str, target: str
) -> Optional[List[str]]:
    """Find a path between two nodes in a directed graph.

    Args:
        graph: NetworkX directed graph
        source: Source node identifier
        target: Target node identifier

    Returns:
        List of nodes representing the path, or None if no path exists
    """
    try:
        return nx.shortest_path(graph, source, target)
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return None


def find_all_paths(
    graph: nx.DiGraph, source: str, target: str, cutoff: Optional[int] = None
) -> List[List[str]]:
    """Find all paths between two nodes up to a maximum depth.

    Args:
        graph: NetworkX directed graph
        source: Source node identifier
        target: Target node identifier
        cutoff: Maximum path length (None for unlimited)

    Returns:
        List of paths (each path is a list of nodes)
    """
    try:
        return list(nx.all_simple_paths(graph, source, target, cutoff=cutoff))
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return []


def has_path(graph: nx.DiGraph, source: str, target: str) -> bool:
    """Check if a path exists between two nodes.

    Args:
        graph: NetworkX directed graph
        source: Source node identifier
        target: Target node identifier

    Returns:
        True if path exists, False otherwise
    """
    return nx.has_path(graph, source, target)


def get_reachable_nodes(graph: nx.DiGraph, source: str) -> Set[str]:
    """Get all nodes reachable from a given source node.

    Args:
        graph: NetworkX directed graph
        source: Source node identifier

    Returns:
        Set of reachable node identifiers
    """
    return set(nx.descendants(graph, source)) | {source}


def get_incoming_edges(graph: nx.DiGraph, node: str) -> List[Tuple[str, str]]:
    """Get all incoming edges to a node.

    Args:
        graph: NetworkX directed graph
        node: Node identifier

    Returns:
        List of (source, target) tuples
    """
    return list(graph.in_edges(node))


def get_outgoing_edges(graph: nx.DiGraph, node: str) -> List[Tuple[str, str]]:
    """Get all outgoing edges from a node.

    Args:
        graph: NetworkX directed graph
        node: Node identifier

    Returns:
        List of (source, target) tuples
    """
    return list(graph.out_edges(node))


def find_cycles(graph: nx.DiGraph) -> List[List[str]]:
    """Find all cycles in a directed graph.

    Args:
        graph: NetworkX directed graph

    Returns:
        List of cycles (each cycle is a list of nodes)
    """
    try:
        return list(nx.simple_cycles(graph))
    except nx.NetworkXError:
        return []


def is_acyclic(graph: nx.DiGraph) -> bool:
    """Check if a directed graph is acyclic.

    Args:
        graph: NetworkX directed graph

    Returns:
        True if graph is DAG (acyclic), False otherwise
    """
    return nx.is_directed_acyclic_graph(graph)


def get_node_attribute(
    graph: nx.DiGraph, node: str, attribute: str, default: Optional[str] = None
) -> Optional[str]:
    """Get an attribute value from a node.

    Args:
        graph: NetworkX directed graph
        node: Node identifier
        attribute: Attribute name
        default: Default value if attribute not found

    Returns:
        Attribute value or default
    """
    if node not in graph:
        return default
    return graph.nodes[node].get(attribute, default)


def set_node_attribute(graph: nx.DiGraph, node: str, attribute: str, value: str) -> None:
    """Set an attribute value on a node.

    Args:
        graph: NetworkX directed graph
        node: Node identifier
        attribute: Attribute name
        value: Attribute value
    """
    if node not in graph:
        graph.add_node(node)
    graph.nodes[node][attribute] = value


def get_edge_attribute(
    graph: nx.DiGraph,
    source: str,
    target: str,
    attribute: str,
    default: Optional[str] = None,
) -> Optional[str]:
    """Get an attribute value from an edge.

    Args:
        graph: NetworkX directed graph
        source: Source node identifier
        target: Target node identifier
        attribute: Attribute name
        default: Default value if attribute not found

    Returns:
        Attribute value or default
    """
    if not graph.has_edge(source, target):
        return default
    return graph.edges[source, target].get(attribute, default)


def set_edge_attribute(
    graph: nx.DiGraph, source: str, target: str, attribute: str, value: str
) -> None:
    """Set an attribute value on an edge.

    Args:
        graph: NetworkX directed graph
        source: Source node identifier
        target: Target node identifier
        attribute: Attribute name
        value: Attribute value
    """
    if not graph.has_edge(source, target):
        graph.add_edge(source, target)
    graph.edges[source, target][attribute] = value
