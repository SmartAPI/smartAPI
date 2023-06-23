import logging
import textwrap
import xml.etree.ElementTree as ET

logger = logging.getLogger("metakg_export")

"""
Functions for metakg data formatting

    edges2graphml() - edge data to graphml formatting

"""

def edges2graphml(chunk, _id, api_call, edge_default="directed"):
    """
    Build a graphML (xml) tree
    Input:
        chunk: data chunk received by the api call
        _id:            dataset ID
        api_call:       the api call
        edge_default:   directed or undirected graph(for graph building), default='directed'
    Returns: 
        graphml_string: a graphml (xml) string 
                        -- automatically downloads file unless, &download=False, flag is added
    Notes:
        * summary info, data size, and warning comments added to the top of the file
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

    # Set the summary text
    summary_text = f"This edge data (ID:{_id}) has been transformed into GraphML format. Curated from SmartAPIs meta knowledge database, the full API path can be seen here: {api_call}."
    # Set the data length comment text
    data_length_text = f"Edge Count: {len(edges)}"

    # Wrap the summary text
    wrapped_summary_text = textwrap.fill(summary_text, width=100)
    # Place both texts into a comment
    comment_element = f"<!-- {wrapped_summary_text} -->\n<!-- {data_length_text} -->\n"

    # Check if the total data hits exceeds the API size limit
    if expected_total > 5000:
        # If the expected total is greater than the size limit, 5000, data has been truncated
        warning_text = f'WARNING: total data size has been truncated to size {len(edges)}. The total data size expected, {expected_total}, exceeds the API size limit (&size=5000).'
        wrapped_warning_text = textwrap.fill(warning_text, width=100)
        warning_comment_element = f"<!-- {wrapped_warning_text} -->\n"
        # Concatenate comment with the graphml string
        graphml_string_with_comment = comment_element + warning_comment_element + graphml_string
    elif expected_total != len(edges):
        # If the expected total isn't equal to the total hits that are returned (edges),
        # give a warning comment for the user.
        warning_text = f'WARNING: the size total of the edges (data hits) given, {len(edges)}, does not equal the expected size of the API, {expected_total}. Try increasing the size parameter, &size=5000.'
        wrapped_warning_text = textwrap.fill(warning_text, width=100)
        warning_comment_element = f"<!-- {wrapped_warning_text} -->\n"
        # Concatenate comment with the graphml string
        graphml_string_with_comment = comment_element + warning_comment_element + graphml_string
    else:
        # Concatenate comment with the graphml string
        graphml_string_with_comment = comment_element + graphml_string

    return graphml_string_with_comment
