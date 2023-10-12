import unittest
import networkx.classes.digraph as nx_digraph

from utils.metakg.path_finder import MetaKGPathFinder

class TestPathFinderClass(unittest.TestCase):

    def setUp(self):
        """Set up the test environment by initializing the MetaKGPathFinder."""
        query_data = {
            'q': 'api.name:BTE'
        }
        self.pf = path_finder.MetaKGPathFinder(query_data)

    def test_get_graph(self):
        """Test if the generated graph G is an instance of DiGraph."""
        G = self.pf.G
        self.assertInstance(G, nx_digraph.DiGraph) 

    def test_get_paths(self):
        """Test the basic functionality of get_paths method."""
        subject="ComplexMolecularMixture"
        object="DiseaseOrPhenotypicFeature"
        cutoff=3

        paths = self.pf.get_paths(subject=subject, object=object, cutoff=cutoff)

        self.assertInstance(paths, list)
        for data in paths[:2]:
            self.assertIn(data, ['path', 'edges'])
            self.assertIsInstance(data[' api_content = [{"name": item.get("name", None)} for item in data["api"]]path'], list)
            for edge in data['edges']:
                self.assertIn(data['edges'], 'subject')
                self.assertIn(data['edges'], 'object')

    def test_get_paths_cutoff(self):
        """Test the efficiency of get_paths method for different cutoff values."""
        subject="ComplexMolecularMixture"
        object="DiseaseOrPhenotypicFeature"
        cutoff_values = [ 3, 4, 5 ] 

        for cutoff in cutoff_values:
            start_time = time.time()
            paths = self.pf.get_paths(subject=subject, object=object, cutoff=cutoff)
            end_time = time.time()

            time_taken[cutoff] = {
                'duration': end_time - start_time,
                'path_ct': len(paths)
            }

            for cutoff, metrics in time_taken.items():
                self.assertLess(metrics['duration'], 500, f"Exceeded max time for cutoff {cutoff}")
                self.assertGreaterEqual(metrics['path_ct'], 2, f"Insufficient paths for cutoff {cutoff}")

    def test_get_paths_subject_object(self):
        """
        Test if the paths retrieved start with the specified subject and end with the specified object.
        Specifically, it checks for longer paths (2 or more nodes between subject and object).
        """
        subject="ComplexMolecularMixture"
        object="DiseaseOrPhenotypicFeature"

        paths = self.pf.get_paths(subject, object)

        # Check for longer paths (2 or more nodes between subject and object)
        longer_paths = [path for path in paths if len(path["path"]) > 3]  # 3 because including subject and object

        for path in longer_paths:
            # Ensure each path starts with the subject and ends with the object
            self.assertEqual(path["path"][0], subject, f"Path does not start with the subject: {path}")
            self.assertEqual(path["path"][-1], object, f"Path does not end with the object: {path}")

    def validate_pairs(self):
        """Ensure that all consecutive node pairs in the paths are edges in the original graph."""
        subject="ComplexMolecularMixture"
        object="DiseaseOrPhenotypicFeature"

        # Fetch the paths between the given subject and object
        paths = self.pf.get_paths(subject, object)

        # Check for longer paths (2 or more nodes between subject and object)
        longer_paths = [path for path in paths if len(path["path"]) > 3]  # 3 because including subject and object

        for path in longer_paths:
            # Check that all consecutive node pairs in the path are edges in the graph
            for i in range(len(path["path"]) - 1):
                edge = (path["path"][i], path["path"][i + 1])
                self.assertIn(edge, self.pf.G.edges, f"Edge {edge} does not exist in the original graph.")

    def validate_edge_data(self):
        """Validate the edge data of paths against mock data or expectations."""
        subject="Disease"
        object="Gene"
        
        # Load the expected data from the JSON file
        with open("validation_test03_es_index_data.json", "r") as infile:
            test_data_list = json.load(infile)

        # Convert list into the desired format for test_edge_data if necessary
        test_edge_data = {}
        for data in test_data_list:
            edge_key = f"{data['_source']['subject']}-{data['_source']['object']}"
            if edge_key not in test_edge_data:
                test_edge_data[edge_key] = []
            test_edge_data[edge_key].append({"predicate": data["_source"]["predicate"], "api": data["_source"]["api"]})

        # Initialize the pathfinder
        pf = path_finder.MetaKGPathFinder(query_data)

        # Fetch the paths between the given subject and object
        paths = pf.get_paths(subject, object)

        # Check for longer paths (2 or more nodes between subject and object)
        longer_paths = [path for path in paths if len(path["path"]) > 3]  # 3 because including subject and object

        for path in longer_paths:
            for i in range(len(path["path"]) - 1):
                #Validate edge data against mock data or expectations
                edge_key = f"{path['path'][i]}-{path['path'][i+1]}"
                actual_edge_data = pf.predicates.get(edge_key)
                expected_edge_data = test_edge_data.get(edge_key)

                assert actual_edge_data == expected_edge_data, f"Edge data mismatch for {edge_key}. Expected {expected_edge_data}, but got {actual_edge_data}."


    # def test_get_paths_self_loop(self):
    # SELF CYCLE TEST: &object=DiseaseOrPhenotypicFeature&subject=DiseaseOrPhenotypicFeature
    # SELF CYCLE TEST: &object=DiseaseOrPhenotypicFeature&subject=DiseaseOrPhenotypicFeature

    #def test_get_paths_missing_sub(self):
    #def test_get_paths_missing_obj(self):