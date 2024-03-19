import networkx as nx

from controller.metakg import MetaKG
from model import ConsolidatedMetaKGDoc


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
            api = doc["_source"]["api"]

            # Add the subject & object to the graph
            self.G.add_edge(subject, object)

            # Add the predicate with api data to a dict based on the node relation
            key = f"{subject}-{object}"
            if key not in predicates:
                predicates[key] = []
            predicates[key].append({"predicate": predicate, "api": api})  # Store both predicate and API

        return self.G

    def build_results(self, paths_data, data, api_details, source_node, target_node):
        # Case: Give full api results in response
        if api_details:
            api_content = data["api"]
        else:
            api_content = [{"name": item.get("name", None), "smartapi": {"id": item["smartapi"]["id"]}} for item in data["api"]]
        paths_data["edges"].append(
            {
                "subject": source_node,
                "object": target_node,
                "predicate": data["predicate"],
                "api": api_content,
            }
        )
        return paths_data

    def get_paths(self, expanded_fields, cutoff=3, api_details=False, predicate_filter=None, edge_filter=None):
        """
        Find all simple paths between expanded subjects and objects in the graph.

        Parameters:
        - expanded_fields: dict
            The expanded fields containing lists of subjects and objects.
        - cutoff: int (default=3)
            The maximum length for any path returned.
        - api_details: bool (default=False)
            If True, includes full details of the 'api' in the result.

        Returns:
        - all_paths_with_edges: list of dict
            A list containing paths and their edge information for all subject-object pairs.
        """

        all_paths_with_edges = []

        # Convert predicate_filter to a set for faster lookups if it's not None
        predicate_filter_set = set(predicate_filter) if predicate_filter else None

        # Iterate over all combinations of subjects and objects
        for subject in expanded_fields["subject"]:
            for object in expanded_fields["object"]:
                if nx.has_path(self.G, subject, object):
                    raw_paths = nx.all_simple_paths(self.G, source=subject, target=object, cutoff=cutoff)
                    for path in raw_paths:
                        paths_data = {"path": path, "edges": []}
                        for i in range(len(path) - 1):
                            source_node = path[i]
                            target_node = path[i + 1]
                            edge_key = f"{source_node}-{target_node}"
                            edge_data = self.predicates.get(edge_key, [])

                            for data in edge_data:
                                # Case: Filter edges based on predicate
                                if predicate_filter_set and data["predicate"] not in predicate_filter_set:
                                    continue # Skip this edge
                                paths_data = self.build_results(paths_data, data, api_details, source_node, target_node)    

                                all_paths_with_edges.append(paths_data)

        return all_paths_with_edges
