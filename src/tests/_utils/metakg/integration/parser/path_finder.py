import unittest
import networkx.classes.digraph as nx_digraph

from utils.metakg.path_finder import MetaKGPathFinder

class TestPathFinderClass(unittest.TestCase):

    def test_get_graph(self):
        query_data = {
            'q': 'api.name:BTE'
        }

        pf = path_finder.MetaKGPathFinder(query_data)
        G = pf.G

        self.assertInstance(G, nx_digraph.DiGraph) 

    def test_get_paths(self):
        subject="ComplexMolecularMixture"
        object="DiseaseOrPhenotypicFeature"
        cutoff=3
        query_data = {
            'q': 'api.name:BTE'
        }

        pf = path_finder.MetaKGPathFinder(query_data)
        paths = pf.get_paths(subject=subject, object=object, cutoff=cutoff)
        self.assertInstance(paths, list)
        for data in paths[:2]:
            self.assertIn(data, ['path', 'edges'])
            self.assertIsInstance(data['path'], list)
            for edge in data['edges']:
                self.assertIn(data['edges'], 'subject')
                self.assertIn(data['edges'], 'object')


    # Test Cutoff values
    #def test_get_paths_cutoff(self):
        # cutoff_values = [ 3, 4, 5 ] 

        # for cutoff in cutoff_values:
        #     start_time = time.time()
        #     paths = pf.get_paths(subject=subject, object=object, cutoff=cutoff)
        #     end_time = time.time()

        #     time_taken[cutoff] = {
        #         'duration': end_time - start_time,
        #         'path_ct': len(paths)
        #     }

    #def test_get_paths_self_loop(self):
    # SELF CYCLE TEST: &object=DiseaseOrPhenotypicFeature&subject=DiseaseOrPhenotypicFeature
    # SELF CYCLE TEST: &object=DiseaseOrPhenotypicFeature&subject=DiseaseOrPhenotypicFeature

    #def test_get_paths_missing_sub(self):
    #def test_get_paths_missing_obj(self):