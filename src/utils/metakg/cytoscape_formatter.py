"""
    Transform ES hits to a cytoscape-ready data format used to render a network graph with &format=html

"""

class CytoscapeDataFormatter():
    """
        Accepts a chunk of ES results and returns them cytoscape compatible format
        that contains all available Nodes and Edges.
        Node:
        {
            'data': { 'id': 'A', 'weight': 1, 'label': 'EntityName' }
        }
        Edge:
        {
            'data': { 'id': 'AB', 'source': 'A', 'target': 'B', 'apis': '[<api_list>]' }
        }

    """

    def __init__(self, chunk):
        self.hits = chunk
        self.node_ids = []
        self.nodes = []
        self.edges = []

    def add_node(self, entity_name):
        if not entity_name in self.node_ids:
            self.node_ids.append(entity_name)
            self.nodes.append({
                'group': 'nodes',
                'data': {
                    'id': entity_name,
                    'weight': 1,
                    'label': entity_name,
                    'colors': "#df4bfc #4a148c"
                }
            })

    def add_edge(self, sub, obj, predicate,  apis):
        self.edges.append({
            'group': 'edges',
            'data': { 
                'id': predicate + sub + obj,
                'source': sub, 'target': obj,
                'predicate': predicate,
                'apis': apis,
                'color': 'black'
            }
        })

    def get_data(self):
        for edge in self.hits:
            self.add_node(edge['subject'])
            self.add_node(edge['object'])
            self.add_edge(edge['subject'], edge['object'], edge['predicate'], edge['api'])
        return self.nodes + self.edges
