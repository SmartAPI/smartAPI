import logging
from warnings import WarningMessage
import xml.etree.ElementTree as ET
import textwrap

from controller import SmartAPI

logger = logging.getLogger("metakg_export")

"""
Export edge data into graphml format
"""

def edges2graphml(chunk, _id, api_call, edge_default="directed"):
    """
    Build a graphML (xml) tree
    Input:
        chunk: list of dictionaries representing a knowledge graph with subject/object/predicate keys
        _id: dataset ID
        api_call: the API path
        edge_default: directed or undirected graph, default='directed'
    Returns: a graphml (xml) string -- automatically downloads file unless, &download=False, flag is added
    Notes:
        * summary info, data total size (edge size), and warning comments 
        were added to the top of the file
    """
    edges = chunk['hits']
    expected_total = chunk['total']
    
    root = ET.Element('graphml') # set root
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

    # tree = ET.ElementTree(root)
    graphml_string = ET.tostring(root, encoding="utf-8", method="xml").decode()

    # Write Comments to top of file
    # set the summary text
    summary_text = f"This edge data (ID:{_id}) has been transformed into GraphML format. Curated from SmartAPIs meta knowledge database, the full API path can be seen here: {api_call}."
    # set the data length comment text
    data_length_text = f"Edge Count: {len(edges)}"    
    # wrap the summary text
    wrapped_summary_text = textwrap.fill(summary_text, width=100)
    # place both texts into a comment
    comment_element = f"<!-- {wrapped_summary_text} -->\n<!-- {data_length_text} -->\n"

    # add a warning comment if the total data hits (chunk['hits]) isn't equal to chunk['total']
    if expected_total > 5000: 
        # if the expected total is greater than the size limit, 5000, data has been truncated
        warning_text =  f'WARNING: total data size has been truncated to size {len(edges)}. The total data size expected, {expected_total}, exceeds the API size limit (&size=5000).'
        wrapped_warning_text = textwrap.fill(warning_text, width=100)
        warning_comment_element = f"<!-- {wrapped_warning_text} -->\n"
        # concat comment with the graphml string 
        graphml_string_with_comment = comment_element + warning_comment_element + graphml_string
    elif expected_total != len(edges):
        # if the expected total isn't equal to the total hits that are returned(edges),
        # give a warning comment for the user.
        warning_text = f'WARNING: the size total of the edges(data hits) given, {len(edges)}, does not equal the expected size of the API, {expected_total}.'
        wrapped_warning_text = textwrap.fill(warning_text, width=100)
        warning_comment_element = f"<!-- {wrapped_warning_text} -->\n"
        # concat comment with the graphml string 
        graphml_string_with_comment = comment_element + warning_comment_element + graphml_string
    else:
        # concat comment with the graphml string 
        graphml_string_with_comment = comment_element + graphml_string


    return graphml_string_with_comment
