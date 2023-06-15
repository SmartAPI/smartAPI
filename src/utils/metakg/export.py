import logging
import xml.etree.ElementTree as ET

from controller import SmartAPI

logger = logging.getLogger("metakg_export")


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

def edges2graphml(edges, edge_default="directed"):
    """
    Build a graphML (xml) tree
    Input:
        edges: list of dictionaries representing a knowledge graph with subject/object/predicate keys
        edge_default: directed or undirected graph, default='directed'
    Returns: a graphml (xml) tree -- will also write to file if outfile name passed
    """
    root = ET.Element('graphml')
    root.set('xmlns', 'http://graphml.graphdrawing.org/xmlns')

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
