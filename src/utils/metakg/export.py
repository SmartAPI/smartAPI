import logging
import textwrap
import xml.etree.ElementTree as ET

logger = logging.getLogger("metakg_export")

"""
Functions for metakg data formatting

    edges2graphml() - edge data to graphml formatting

"""

def edges2graphml(chunk, api_call, protocol, host, edge_default="directed"):
    """
    Build a graphML (xml) tree
    Input:
        chunk: data chunk received by the api call
        api_call:       the api call
        protocol:       server address
        host:           host address
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
    title_text=f'''This GraphML export was generated from this SmartAPI MetaKG (Meta KnowledgeGraph) query:'''
    api_call_text=f'''{protocol}://{host}{api_call}'''
    note01_text=f'''You can also change "format=graphml" parameter to "format=json" to view a JSON output, or "format=html" to view a visualization of the filtered MetaKG based on your query criteria.'''
    summary_title_text=f'''Summary of the filtered MetaKG:'''
    edges_matched_text=f'''* Total no. of edges matched: {chunk['total']}'''
    edges_export_text=f'''* Total no. of edges exported: {len(edges)}'''
    nodes_export_text=f'''* Total no. of nodes exported: ###'''
    # Wrap the summary text
    wrapped_title_text = textwrap.fill(title_text, width=100)
    wrapped_note_text = textwrap.fill(note01_text, width=100)

    # successful matching case - api query batch size matches the expected query size
    if expected_total == len(edges):
        # Place both texts into a comment
        comment_element = f"<!-- {wrapped_title_text} \n\n \t{api_call_text} \n\n {wrapped_note_text} \n\n {summary_title_text} \n\n\t{edges_matched_text} \n\t{edges_export_text} \n\t{nodes_export_text} \n-->\n\n"
        # Concatenate comment with the graphml string
        graphml_string_with_comment = comment_element + graphml_string
    else:
        # expected query size is greater than api limit (5000)
        if expected_total > 5000:
            warning_text = f' WARNING: the total no. of edges matching your query are over our maximal export limit of 5000. To retrive all mathcing edges, you may use the "from" and "size" to paginate the export and manually concatenate them together.'
        elif expected_total > len(edges):
            warning_text = f' WARNING: the exported edges ({len(edges)}) are less than total no. of edges matching your query ({expected_total}). To export all matching edges, you may increase your "size" parameter (up to 5000).'            
        wrapped_warning_text = textwrap.fill(warning_text, width=100)
        # Place both texts into a comment
        comment_element = f"<!-- {wrapped_title_text} \n\n \t{api_call_text} \n\n {wrapped_note_text} \n\n {summary_title_text} \n\n\t{edges_matched_text} \n\t{edges_export_text} \n\t{nodes_export_text} \n\n{wrapped_warning_text} \n-->\n\n"
        # Concatenate comment with the graphml string
        graphml_string_with_comment = comment_element + graphml_string

    return graphml_string_with_comment
