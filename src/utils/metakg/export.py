import logging
import xml.etree.ElementTree as ET

from controller import SmartAPI

logger = logging.getLogger("metakg_export")

"""
Export edge data into graphml format
"""

def compare_hits(mkg_id, hits_total, predicate=None):
    """
    Get MetaKG API
        - using built-in smartapi funcitons, get & return a datasets metakg api 
        Input:
            mkg_id: string id of the requested api
            predicate: (optional) string of a requested predicate, default None
        Returns: 
            True - if the given API hits total equal the tested hits total, or
            False - if the given API hits do not equal the tested hits total
    """
    api = SmartAPI.get(mkg_id)
    test_hits = api.get_metakg()
    print("LENGTH: ", len(test_hits))
    if predicate:
        test_hits =[d for d in test_hits if d['predicate'] == predicate]
    if len(test_hits) == hits_total:
        logger.info("Full data being retrieved, data is sufficient")
        return True
    else:
        logger.warning('Data hits retrieved do not match, API call retrieved %s, and test retrieval has %s'%(hits_total, len(test_hits)))
        return False

def write_graphml(tree, filename=None):
    """
    Output graphML file
        Input: 
            tree: graphml (xml) tree
            outfile: graphml file name, i.e "mygraph.graphml"
        Returns:
            Writes graphml file, else raises error.
    """
    if filename:
        tree.write(filename)
    else:
        logger.info('[write_graphml] no filename given')

def edges2graphml(edges, q_id, api_call, edge_default="directed"):
    """
    Build a graphML (xml) tree
    Input:
        edges: list of dictionaries representing a knowledge graph with subject/object/predicate keys
        q_id: dataset ID
        api_call: the API path
        edge_default: directed or undirected graph, default='directed'
    Returns: a graphml (xml) string -- automatically downloads file unless, &download=False, flag is added
    Notes:
        * added information comments to the top of the file
        * added data hits total to the top of the file
    - Do we want to make the edge default direction customizable?
    """

    root = ET.Element('graphml')
    root.set('xmlns', 'http://graphml.graphdrawing.org/xmlns')

    # Add comment with data length
    comment_data = ET.Comment(f"This edge data (ID:{q_id}) has been transformed into GraphML format, with edge default={edge_default}. The full API path called - {api_call}.")
    comment_data_length = ET.Comment(f"Edge Count: {len(edges)}")
    root.append(comment_data)
    root.append(comment_data_length)
    
    # Define key for node data
    key_node = ET.SubElement(root, 'key')
    key_node.set('id', 'd1')
    key_node.set('for', 'node')
    key_node.set('attr.name', 'label')
    key_node.set('attr.type', 'string')

    # Define key for edge data
    key_edge = ET.SubElement(root, 'key')
    key_edge.set('id', 'd2')
    key_edge.set('for', 'edge')
    key_edge.set('attr.name', 'label')
    key_edge.set('attr.type', 'string')
    graph = ET.SubElement(root, 'graph')
    graph.set('id', 'G')
    graph.set('edgedefault', edge_default) #directed/undirected

    # iterate over edges and fill in data
    for data in edges:
        node = ET.SubElement(graph, 'node')
        node.set('id', data['subject'])
        
        data_node = ET.SubElement(node, 'data')
        data_node.set('key', 'd1')
        data_node.text = data['subject']
        
        edge = ET.SubElement(graph, 'edge')
        edge.set('source', data['subject'])
        edge.set('target', data['object'])
        
        data_edge = ET.SubElement(edge, 'data')
        data_edge.set('key', 'd2')
        data_edge.text = data['predicate']

    tree = ET.ElementTree(root)
    graphml_string = ET.tostring(root, encoding="utf-8", method="xml").decode()
    
    return graphml_string
