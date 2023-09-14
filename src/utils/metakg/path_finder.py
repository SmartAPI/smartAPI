import networkx as nx

from controller.metakg import MetaKG
from controller.smartapi import SmartAPI
from model import ConsolidatedMetaKGDoc

class MetaKGPathFinder:

    def __init__(self, query_data=None):
        self.get_graph(query_data)
        self.predicates = {}

    def get_graph(self, query_data=None):
        """
        Make a networkx graph by traversing the index documents and extract targeted nodes/edges
        """
        index = ConsolidatedMetaKGDoc.Index.name

        # Create a new directed graph
        self.G = nx.DiGraph()

        # Scroll through qsearch results with direct call to index
        for doc in MetaKG.get_all_via_scan(size=1000, query_data=query_data, index=index): 
            # Extract subject, object, and predicate from hit
            subject = doc['_source']['subject']
            object = doc['_source']['object']
            predicate =doc['_source']['predicate']

            self.G.add_edge(subject, object)
            
            key = f"{subject}-{object}"
            if key not in predicates:
                self.predicates[key] = []
            self.predicates[key].append(predicate)

        return self.G

    def get_paths(self, subject, object, cutoff=3, verbose=False):
        paths_with_data = []

        if nx.has_path(G, source, target):
            raw_paths = list(nx.all_simple_paths(G, source=subject, target=object, cutoff=cutoff))
            for path in raw_paths:
                paths_data = {
                    "path": path,
                    "edges": []
                }

                for i in range(len(path) - 1):
                    source_node = path[i]
                    target_node = path[i + 1]
                    edge_data = self.get_pathaway_predicates(subject, object)
                    paths_data["edge_data"].append({
                        "subject": source_node,
                        "object": target_node,
                        "predicates": edge_data
                    })

                paths_with_data.append(paths_data)

            if verbose:
                print(f"Pathways Extracted: {len(raw_paths)}")
                for idx, data in enumerate(paths_with_data):
                    print(f"Path {idx}:", " -> ".join(data["path"]))
                    for edge in data["edge_data"]:
                        print(f'\n * {edge["source"]} -> {edge["target"]} * \nEdges: {", ".join(edge["edges"])}')
                    print("\n" + "-"*80 + "\n")

        return paths_with_data
