import pytest
from utils.metakg.path_finder import MetaKGPathFinder
import networkx as nx

def test_init():
    # Test initialization with default parameters
    path_finder = MetaKGPathFinder()
    print("Test 1")
    # assert path_finder.predicates == {}
    assert path_finder.expanded_fields == {"subject": [], "object": []}

    # Test initialization with custom parameters
    query_data = {"q": "api.name:BTE"}
    test_subject = "Virus"
    test_object = "Drug"
    path_finder = MetaKGPathFinder(query_data=query_data, expanded_fields={"subject": [test_subject], "object": [test_object]})
    # assert path_finder.predicates != {}
    assert path_finder.expanded_fields == {"subject": [test_subject], "object": [test_object]}

def test_get_graph():
    # Test get_graph with default parameters
    path_finder = MetaKGPathFinder()
    graph = path_finder.get_graph()
    assert isinstance(graph, nx.DiGraph)

    # Test get_graph with custom parameters
    query_data = {"q": "api.name:BTE"}
    path_finder = MetaKGPathFinder(query_data=query_data)
    graph = path_finder.get_graph(query_data=query_data)
    assert isinstance(graph, nx.DiGraph)

def test_build_edge_results():
    path_finder = MetaKGPathFinder()
    paths_data = {"path": ["Virus", "Drug"], "edges": []}
    data = {"predicate": "p1", "api": [{"name": "api1", "smartapi": {"id": "id1"}}]}
    api_details = False
    source_node = "Virus"
    target_node = "Drug"
    paths_data = path_finder.build_edge_results(paths_data, data, api_details, source_node, target_node)
    assert paths_data["edges"][0]["subject"] == source_node
    assert paths_data["edges"][0]["object"] == target_node
    assert paths_data["edges"][0]["predicate"] == data["predicate"]
    assert paths_data["edges"][0]["api"][0]["api"]["name"] == data["api"][0]["name"]

def test_get_paths():
    path_finder = MetaKGPathFinder(expanded_fields={"subject": ["Virus"], "object": ["Drug"]})
    paths = path_finder.get_paths()
    assert isinstance(paths, list)
    if paths:  # If there are any paths, check the first one
        assert "path" in paths[0]
        assert "edges" in paths[0]

def test_expand():
    ...