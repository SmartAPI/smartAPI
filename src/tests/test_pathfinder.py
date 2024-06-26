"""
    Test cases for the MetaKGPathFinder class
    /src/utils/metakg/path_finder.py
"""

from utils.metakg.path_finder import MetaKGPathFinder
import networkx as nx

def test_init():
    # Test initialization with default parameters
    path_finder = MetaKGPathFinder()
    assert path_finder.predicates != {}
    assert path_finder.expanded_fields == {"subject": [], "object": []}

    # Test initialization with custom parameters
    query_data = {"q": "api.name:BTE"}
    test_subject = "Virus"
    test_object = "Drug"
    path_finder = MetaKGPathFinder(query_data=query_data, expanded_fields={"subject": [test_subject], "object": [test_object]})
    assert path_finder.predicates != {}
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
    data = {"predicate": "has_part", "api": [{"name": "api1", "smartapi": {"id": "id1"}}]}
    api_details = False
    source_node = "Virus"
    target_node = "Drug"
    bte=0
    paths_data = path_finder.build_edge_results(paths_data, data, api_details, source_node, target_node, bte)
    assert paths_data["edges"][0]["subject"] == source_node
    assert paths_data["edges"][0]["object"] == target_node
    assert paths_data["edges"][0]["predicate"] == data["predicate"]
    assert paths_data["edges"][0]["api"][0]["api"]["name"] == data["api"][0]["name"]

def test_get_paths_default():
    path_finder = MetaKGPathFinder(expanded_fields={"subject": ["Virus"], "object": ["Drug"]})
    paths = path_finder.get_paths()
    assert isinstance(paths, list)
    if paths:
        assert "path" in paths[0]
        assert "edges" in paths[0]

def test_get_paths_subject():
    path_finder = MetaKGPathFinder(expanded_fields={"subject": ["Virus"], "object": ["Drug"]})
    paths = path_finder.get_paths()
    assert isinstance(paths, list)
    if paths:
        assert "path" in paths[0]
        assert paths[0]["path"][0] == "Virus"

def test_get_paths_object():
    path_finder = MetaKGPathFinder(expanded_fields={"subject": ["Virus"], "object": ["Drug"]})
    paths = path_finder.get_paths()
    assert isinstance(paths, list)
    if paths:
        assert "path" in paths[0]
        assert paths[0]["path"][-1] == "Drug"

def test_get_paths_cutoff():
    path_finder = MetaKGPathFinder(expanded_fields={"subject": ["Virus"], "object": ["Drug"]})
    paths = path_finder.get_paths(cutoff=3)
    assert isinstance(paths, list)
    if paths:
        assert "path" in paths[0]
        assert "edges" in paths[0]
        # add more verbsoe test for cutoff

def test_get_paths_api_details():
    path_finder = MetaKGPathFinder(expanded_fields={"subject": ["Virus"], "object": ["Drug"]})
    paths = path_finder.get_paths(api_details=True)
    assert isinstance(paths, list)
    if paths:
        assert "path" in paths[0]
        assert "edges" in paths[0]
        assert "api" in paths[0]["edges"][0]

def test_get_paths_predicate_filter():
    path_finder = MetaKGPathFinder(expanded_fields={"subject": ["Virus"], "object": ["Drug"]})
    paths = path_finder.get_paths(predicate_filter=["has_part"])
    assert isinstance(paths, list)
    if paths:
        assert "path" in paths[0]
        assert "edges" in paths[0]
        assert all(edge["predicate"] == "has_part" for edge in paths[0]["edges"])

def test_get_paths_bte():
    path_finder = MetaKGPathFinder(expanded_fields={"subject": ["Virus"], "object": ["Drug"]})
    paths = path_finder.get_paths(bte=True)
    assert isinstance(paths, list)
    if paths:
        assert "path" in paths[0]
        assert "edges" in paths[0]
        edge = paths[0]["edges"][0]
        assert "api" in edge
        api = edge["api"][0]
        assert "bte" in api
        bte = api["bte"]
        assert "query_operation" in bte
        query_operation = bte["query_operation"]
        assert "path" in query_operation
        assert "method" in query_operation
        assert "server" in query_operation
