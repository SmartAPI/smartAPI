import networkx as nx

from controller.metakg import MetaKG
from model import ConsolidatedMetaKGDoc

class MetaKGPathFinder:

    def __init__(self, query_data=None):
        """
        Initialize the MetaKGPathFinder class. 
        
        This class is responsible for creating a network graph from indexed 
        documents and providing functionalities to find paths between two nodes 
        in the graph.
        
        Parameters:
        - query_data: dict (default=None)
            Optional data to filter which documents to use while creating the graph.
        """
        self.predicates = {}
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
        predicates=self.predicates

        # Create a new directed graph
        self.G = nx.DiGraph()

        # Scroll through search results with direct call to index
        for doc in MetaKG.get_all_via_scan(size=1000, query_data=query_data, index=index): 
            # Extract subject, object, and predicate from hit
            subject = doc['_source']['subject']
            object = doc['_source']['object']
            predicate = doc['_source']['predicate']
            api = doc['_source']['api']

            # Add the subject & object to the graph
            self.G.add_edge(subject, object)

            # Add the predicate with api data to a dict based on the node relation
            key = f"{subject}-{object}"
            if key not in predicates:
                predicates[key] = []
            predicates[key].append({"predicate": predicate, "api": api})  # Store both predicate and API

        return self.G

    def get_paths(self, subject, object, cutoff=3, api_details=False):
        """
        Find all simple paths between two nodes in the graph.

        This method retrieves all possible paths between a given subject and 
        object in the graph, up to a specified cutoff length.

        Parameters:
        - subject: str
            The starting node in the graph.
        - object: str
            The ending node in the graph.
        - cutoff: int (default=3)
            The maximum length for any path returned.
        - api_details: bool (default=False)
            If True, the full details of the 'api' are included in the result. 
            If False, only the 'name' attribute of each 'api' entry is retained.

        Returns:
        - paths_with_edges: list of dict
            A list containing paths and their edge information.
        """

        paths_with_edges = []

        if nx.has_path(self.G, subject, object):
            raw_paths = list(nx.all_simple_paths(self.G, source=subject, target=object, cutoff=cutoff))
            for path in raw_paths:
                paths_data = {
                    "path": path,
                    "edges": []
                }

                for i in range(len(path) - 1):
                    source_node = path[i]
                    target_node = path[i + 1]
                    edge_key = f"{source_node}-{target_node}"
                    edge_data = self.predicates.get(edge_key, [])

                    for data in edge_data:
                        # if api_details add full api list, else add selected keys only
                        if api_details:
                            api_content = data["api"]
                        else:
                            api_content = [{"name": item.get("name", None)} for item in data["api"]]
                            print(api_content)
                        paths_data["edges"].append({
                            "subject": source_node,
                            "object": target_node,
                            "predicate": data["predicate"],
                            "api": api_content
                        })

                paths_with_edges.append(paths_data)

        return paths_with_edges