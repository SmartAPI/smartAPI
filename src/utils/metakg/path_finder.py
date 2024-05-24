import networkx as nx
import logging
from controller.metakg import MetaKG
from model import ConsolidatedMetaKGDoc
import traceback
import pprint

logger=logging.basicConfig(level=logging.INFO, filename="missing_bte.log")

class MetaKGPathFinder:
    def __init__(self, query_data=None, expanded_fields=None):
        """
        Initialize the MetaKGPathFinder class.

        Parameters:
        - query_data: dict (default=None)
            Optional data to filter which documents to use while creating the graph.
        - expanded_fields: dict (default=None)
            Optional fields to expand subjects and objects in the graph.
        """
        self.predicates = {}
        self.expanded_fields = expanded_fields or {"subject": [], "object": []}
        self.get_graph(query_data=query_data)

    def get_graph(self, query_data=None):
        """
        Construct a directed graph from the indexed documents in the metakg consolidated index.

        This method traverses the index documents, extracts nodes and edges,
        and uses them to create a directed graph using the networkx library.

        Parameters:
        - query_data: dict (default=None)
            Optional data to filter which documents to use for graph construction.

        Returns:
        - G: nx.DiGraph
            A directed graph constructed from the indexed documents.
        """
        index = ConsolidatedMetaKGDoc.Index.name
        predicates = self.predicates

        # Create a new directed graph
        self.G = nx.DiGraph()

        # Scroll through search results with direct call to index
        for doc in MetaKG.get_all_via_scan(size=1000, query_data=query_data, index=index):
            # Extract subject, object, and predicate from hit
            subject = doc["_source"]["subject"]
            object = doc["_source"]["object"]
            predicate = doc["_source"]["predicate"]
            # make list here to give back full results 
            api = [api_dict for api_dict in doc["_source"]["api"]]
            # Add the subject & object to the graph
            self.G.add_edge(subject, object)

            # Add the predicate with api data to a dict based on the node relation
            key = f"{subject}-{object}"
            if key not in predicates:
                predicates[key] = []
            predicates[key].append({"predicate": predicate, "api": api})  # Store both predicate and API

        return self.G

    def build_edge_results(self, paths_data, data, api_details, source_node, target_node, bte):
        """
        Adds edge details between two nodes to the paths data structure.

        Parameters:
        - paths_data (dict): The paths data structure being built up.
        - data (dict): Data about the edge, including the predicate and APIs.
        - api_details (bool): If True, include full API details; otherwise, include minimal API information.
        - source_node (str): Identifier for the source node of the edge.
        - target_node (str): Identifier for the target node of the edge.

        Returns:
        - dict: The updated paths_data structure with the new edge added.
        """

        apis = data["api"]
        # # Case: Give full api results in response
        if api_details:
            api_content = data["api"]
        else:
            if bte:
                api_content = [{"api": {"name": item.get("name", None), "smartapi": {"id": item["smartapi"]["id"]}}, "bte":item["bte"]} for item in apis]
            else:
                api_content = [{"api": {"name": item.get("name", None), "smartapi": {"id": item["smartapi"]["id"]}}} for item in apis]

        paths_data["edges"].append(
            {
                "subject": source_node,
                "object": target_node,
                "predicate": data["predicate"],
                "api": api_content,
            }
        )

        return paths_data

    def get_paths(self, cutoff=2, api_details=False, predicate_filter=None, bte=False):
        """
        Find all simple paths between expanded subjects and objects in the graph.

        Parameters:
        - expanded_fields: (dict) The expanded fields containing lists of subjects and objects.
        - cutoff: (int, default=2) The maximum length for any path returned.
        - api_details: (bool, default=False) If True, includes full details of the 'api' in the result.
        - predicate_filter: (list, default=None) A list of predicates to filter the results by.

        Returns:
        - all_paths_with_edges: (list of dict) A list containing paths and their edge information for all subject-object pairs.
        """

        all_paths_with_edges = []

        # Predicate Filter Setup
        # Convert predicate_filter to a set for faster lookups if it's not None
        predicate_filter_set = set(predicate_filter) if predicate_filter else None
        # Add predicates from expanded_fields['predicate'] if it exists and is not None
        if 'predicate' in self.expanded_fields and self.expanded_fields['predicate']:
            predicate_filter_set.update(self.expanded_fields['predicate'])

        # Graph Iteration
        # Iterate over all combinations of subjects and objects
        for subject in self.expanded_fields["subject"]:
            for object in self.expanded_fields["object"]:
                try:
                    # Check if a path exists between the subject and object
                    if nx.has_path(self.G, subject, object):
                        raw_paths = nx.all_simple_paths(self.G, source=subject, target=object, cutoff=cutoff)
                        for path in raw_paths:
                            paths_data = {"path": path, "edges": []}
                            edge_added = False  # Flag to track if any edge has been added
                            for i in range(len(path) - 1):
                                source_node = path[i]
                                target_node = path[i + 1]
                                edge_key = f"{source_node}-{target_node}"
                                edge_data = self.predicates.get(edge_key, [])

                                for data in edge_data:
                                    # Case: Filter edges based on predicate
                                    if predicate_filter_set and data["predicate"] not in predicate_filter_set:
                                        continue  # Skip this edge
                                    paths_data = self.build_edge_results(paths_data, data, api_details, source_node, target_node, bte)
                                    edge_added = True  # Mark that we've added at least one edge
                            if edge_added:  # Only add paths_data if at least one edge was added
                                all_paths_with_edges.append(paths_data)
                except Exception as e:
                    print(f"Error: {e} {e.args}")
                    print(traceback.format_exc())
                    continue  # Explicitly continue to the next subject-object pair

        return all_paths_with_edges
