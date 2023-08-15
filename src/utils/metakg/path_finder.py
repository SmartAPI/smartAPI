from controller import SmartAPI

import networkx as nx


class MetaKGPathFinder():
    # get index and grab the networkx graph
    # get the target and the source (& depth, default=3?)
    # return the paths & edges 

    def generate_networkx_graph(index, graph_type="simple_digraph", edges=False):
        index = "smartapi_metakg_docs_consolidated"

        # # Create a new directed graph
        if graph_type == "simple_digraph":
            G = nx.DiGraph()
        elif graph_type == "multi_digraph":
            G = nx.MultiDiGraph()

        # Scroll through search results
        for hit in cls.get_all_via_scan(index): # directly call 
            # Extract subject, object, and predicate from hit
            _subject = hit['_source']['subject']
            _object = hit['_source']['object']
            _predicate = hit['_source']['predicate']
            
            # Add edge to graph, with predicate as an attribute
            if edges is True:
                G.add_edge(_subject, _object, predicate=_predicate)
            else:
                G.add_edge(_subject, _object)

        return G