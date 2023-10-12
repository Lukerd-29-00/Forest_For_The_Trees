import unittest
import graph

class GraphTestCase(unittest.TestCase):

    def test_graph_contains_vertices(self):
        G = graph.Graph(range(5),[])
        for item in range(5):
            self.assertIn(item,G)
        
        G = graph.Graph(map(str,range(5)),[])
        for item in map(str,range(5)):
            self.assertIn(item,G)

    def test_graph_contains_edges(self):
        vertices = ['A', 'B', 'C']
        edges = [('A', 'B'), ('B', 'C')]
        G = graph.Graph(vertices,edges)
        for edge in edges:
            self.assertIn(edge,G)
            self.assertIn((edge[1], edge[0]),G) #Graphs are undirected
        for edge in G.edges:
            self.assertTrue(edge in edges or (edge[1], edge[0])  in edges)


    def test_neighbors(self):
        vertices = ["A", "B", "C", "D"]
        edges = [("A", "B"), ("A", "C"), ("B", "C"), ("C", 'D')]
        G = graph.Graph(vertices,edges)

        Aneighbors = G.neighbors('A')
        self.assertSetEqual(Aneighbors,set(['B','C']))

        Bneighbors = G.neighbors('B')
        self.assertSetEqual(Bneighbors,set(['A','C']))

        Cneighbors = G.neighbors('C')
        self.assertSetEqual(Cneighbors,set(['B', 'D', 'A']))

        Dneighbors = G.neighbors('D')
        self.assertSetEqual(Dneighbors,set(['C']))

    def test_map_vertices(self):
        Vset_1 = ['A', 'B', 'C', 'D']
        edges = [('A', 'B'), ('B', 'C'), ('C', 'D')]
        G0 = graph.Graph(Vset_1,edges)
        i = graph.Isomorphism({'A': 1, 'B': 2, 'C': 3, 'D': 4})
        G1 = G0.map_vertices(i)
        found_edges = list(G1.edges)
        self.assertListEqual(found_edges,[(1,2),(2,3),(3,4)])

    def test_check_automorphism(self):
        Vset = range(4)
        edges = [(0, 1), (1, 2), (2, 0), (2, 3)]
        G = graph.Graph(Vset,edges)
        self.assertTrue(G.is_automorphism(graph.Isomorphism({0: 0, 1: 1, 2: 2, 3: 3})))
        self.assertTrue(G.is_automorphism(graph.Isomorphism({0: 1, 1: 0, 2: 2, 3: 3})))
        self.assertFalse(G.is_automorphism(graph.Isomorphism({0: 3, 3: 0, 1: 1, 2: 2})))

    def test_equality(self):
        G0 = graph.Graph(['A', 'B', 'C', 'D'],[('A','B'), ('A', 'C'), ('B', 'C'), ('C', 'D')])
        G1 = graph.Graph(['A', 'B', 'C', 'D'],[('A','B'), ('A', 'C'), ('B', 'C'), ('C', 'D')])
        self.assertEqual(G0,G1)
        self.assertEqual(G1,G0)
        G1 = graph.Graph(['A', 'B', 'C', 'D', 'E'],[('A','B'), ('A', 'C'), ('B', 'C'), ('C', 'D')])
        self.assertNotEqual(G0,G1)
        self.assertNotEqual(G1,G0)
        G1 = graph.Graph(['A', 'B', 'C', 'D'],[('A','B'), ('A', 'C'), ('B', 'C'), ('C', 'D'), ('B', 'D')])
        self.assertNotEqual(G0,G1)
        self.assertNotEqual(G1,G0)

    def test_graph_serialization(self):
        G0 = graph.Graph(range(7),[(0, 1), (1, 5), (6, 3)])
        G1 = graph.Graph.loads(G0.dumps())
        self.assertEqual(G0,G1)

    def test_copy(self):
        vertices = range(7)
        edges = [(0, 1), (1, 5), (6, 3)]
        G0 = graph.Graph(vertices,edges)
        G1 = G0.copy()
        self.assertEqual(G0,G1)

    def test_isomorphism_add(self):
        i1 = graph.Isomorphism({'A': 'C', 'B': 'D', 'C': 'E'})
        i2 = graph.Isomorphism({'C': 'C', 'D': 'E', 'E': 'D'})
        self.assertDictEqual({
            'A': 'C',
            'B': 'E',
            'C': 'D'
        },(i1+i2)._mapping)

    def test_isomorphism_neg(self):
        i1 = graph.Isomorphism({'A': 'C', 'B': 'D', 'C': 'E'})
        self.assertDictEqual({
            'C': 'A',
            'D': 'B',
            'E': 'C'
        },(-i1)._mapping)

    def test_isomorphism_sub(self):
        i1 = graph.Isomorphism({'A': 'B', 'B': 'C', 'C': 'A'})
        i2 = graph.Isomorphism({'B': 'A', 'C': 'B', 'A': 'C'})
        self.assertDictEqual({
            'A': 'C',
            'B': 'A',
            'C': 'B'
        },(i1-i2)._mapping)

    def test_isomorphsim_serialization(self):
        i1 = graph.Isomorphism({'A': 'B', 'B': 'C', 'C': 'A'})
        i2 = graph.Isomorphism.loads(i1.dumps())
        self.assertDictEqual({
            'A': 'B',
            'B': "C",
            'C': 'A'
        },i2._mapping)

        #make sure serialization works for different data types
        i1 = graph.Isomorphism({0: 1, 1: 2, 2: 0})
        i2 = graph.Isomorphism.loads(i1.dumps())
        self.assertDictEqual({
            0: 1,
            1: 2,
            2: 0
        },i2._mapping)

    def test_pop_edge(self):
        edges = [("A", "B"), ("B", "C"), ("C", "A"), ("D", "E")]
        G = graph.Graph(['A','B','C','D','E'],[("A", "B"), ("B", "C"), ("C", "A"), ("D", "E")])
        self.assertIn(('C', 'A'),G)
        self.assertIn(('A', 'C'),G)
        G.pop(('C','A'))
        edges = [("A", "B"), ("B", "C"), ("D", "E")]
        for e in edges:
            self.assertIn(e,G)
        self.assertNotIn(('C', "A"),G)
        self.assertNotIn(('A', 'C'),G)
        for edge in G.edges:
            self.assertTrue(edge in edges or (edge[1], edge[0]) in edges)


    def test_pop_vertex(self):
        vertices = ['A','B','C','D','E']
        edges = [("A", "B"), ("B", "C"), ("C", "A"), ("D", "E")]
        G = graph.Graph(vertices,edges)
        self.assertIn("A",G)
        self.assertIn(("A","B"),G)
        self.assertIn(("C","A"),G)
        self.assertIn(("B","A"),G)
        self.assertIn(("A","C"),G)

        G.pop("A")

        vertices = ['B','C',"D",'E']
        edges = [('B', 'C'), ('D', 'E')]

        for v in vertices:
            self.assertIn(v,G)
        for v in G.vertices:
            self.assertIn(v,vertices)
        
        for u, v in edges:
            self.assertIn((u, v),G)
        for u, v in G.edges:
            self.assertTrue((u, v) in edges or (v, u) in edges)




if __name__ == "__main__":
    unittest.main()

    