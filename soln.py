import graph
import typing
import json
from pwn import *

HOST = '0.cloud.chals.io'
PORT = 26278

def _is_tree(G: graph.Graph, parent: typing.Optional[int], current: int, visited: typing.Set[int])->bool:
    visited.add(current)
    for child in G.neighbors(current):
        if child in visited and child != parent:
            return False
        elif child not in visited and not _is_tree(G,current,child,visited):
            return False
    return True

def is_tree(G: graph.Graph)->bool:
    return len(G.edges) == (len(G.vertices) - 1)

def is_forest(G: "Forest")->bool:
    visited = set()
    for v in G.vertices:
        if v not in visited and not _is_tree(G,None,v,visited):
            return False
    return True

def cmp_depth_maps(map_1, map_2):
    for k in map_1.keys():
        if k not in map_2.keys() or len(map_1[k]) != len(map_2[k]):
            return False
    for k in map_2.keys():
        if k not in map_1.keys():
            return False
    return True

def del_from_map(mp, v)->None:
    """Retrieive the path_lengths resulting from removing v from the tree that produced mp via path_lengths"""
    mp.pop(v)
    for v2 in mp.keys():
        for k in mp[v2].keys():
            if v in mp[v2][k]:
                mp[v2][k].remove(v)
                break #A vertex can only appear in one depth level

class Forest(graph.Graph):

    def depth_search(self, root)->typing.Iterable[typing.Tuple[int,int]]:
        chain = [(root, iter(self.neighbors(root)))]
        visited = set()
        while chain:
            current, child_gen = chain[-1]
            if current not in visited:
                yield current, len(chain) - 1
                visited.add(current)
            try:
                child = next(child_gen)
                while child in visited:
                    child = next(child_gen)
                chain.append((child,iter(self.neighbors(child))))
            except StopIteration:
                chain.pop()

    def _tree(self, root: int, V: typing.Set[int], E: typing.Set[typing.Tuple[int, int]]):
        V.add(root)
        for child in filter(lambda v: v not in V, self.neighbors(root)):
            #This finds all the edges because the graph is a forest and therefore acyclic.
            E.add((root, child))
            self._tree(child,V,E)

    def path_lengths(self)->typing.Dict[int,typing.Dict[int,typing.Set[int]]]:
        output: typing.Dict[int,typing.Dict[int,typing.Set[int]]] = {}
        for v in self.vertices:
            new_map: typing.Dict[int,typing.Set[int]] = {}
            for v2, depth in self.depth_search(v):
                if depth in new_map.keys():
                    new_map[depth].add(v2)
                else:
                    new_map[depth] = set([v2])
            output[v] = new_map
        return output

    def isomorphic(self, other: "Forest")->bool:
        if len(self.vertices) != len(other.vertices):
            return False
        self_depth_maps = self.path_lengths()
        other_depth_maps = other.path_lengths()

        for v1 in self_depth_maps.keys():
            found = False
            d1 = self_depth_maps[v1]
            for v2 in other_depth_maps.keys():
                d2 = other_depth_maps[v2]
                if cmp_depth_maps(d1,d2):
                    found = True
                    break
            if found:
                other_depth_maps.pop(v2)
            else:
                return False
        return True

    def trees(self):
        visited = set()
        for root in self.vertices:
            if root not in visited:
                V = set()
                E = set()
                self._tree(root,V,E)
                visited = visited.union(V)
                yield Tree(V,E)

    def map_to(self, other: "Forest")->"typing.Optional[graph.Isomorphism]":
        output = {}
        other_trees = list(other.trees())
        for t1 in self.trees():
            found = False
            for i, t2 in enumerate(other_trees):
                mapping = t1.map_to(t2)
                if mapping is not None:
                    output.update(mapping._mapping)
                    found = True
                    break
            if found:
                other_trees.pop(i)
            else:
                return None
        if len(other_trees) == 0:
            return self.isomorphism(output)
        else:
            return None

            
class Tree(Forest):
    def leaves(self)->typing.Iterable[int]:
        for v in self.vertices:
            if len(self.neighbors(v)) <= 1:
                yield v

    def copy(self)->"Tree":
        output = super(Tree,self).copy()
        return Tree(output.vertices,output.edges)
    
    def _find_map(self, root: int, other: "Tree", output: typing.Dict[int,int]):
        #OPTIMIZATION: make this iterative, rather than recursive.
        self_visited = set(output.keys())
        for u in filter(lambda u: u not in self_visited,self.neighbors(root)):
            T1 = self.copy()
            T1.pop(u)
            for v in filter(lambda v: v not in output.values(),other.neighbors(output[root])):
                T3 = other.copy() #OPTIMIZATION: allow inserting vertices and edges to avoid copying entire graphs repeatedly.
                T3.pop(v)
                if T1.isomorphic(T3):
                    break
            output[u] = v
        for v in filter(lambda x: x not in self_visited, self.neighbors(root)):
            self._find_map(v,other,output)
    
    def map_to(self, other: "Tree")->typing.Optional[graph.Isomorphism]:
        if not self.isomorphic(other):
            return None
        
        output = {}
        start = next(iter(self.vertices))
        T1 = self.copy()
        T1.pop(start)
        for v in other.vertices:
            T3 = other.copy() 
            T3.pop(v)
            if T1.isomorphic(T3):
                break
        output[start] = v
        self._find_map(start,other,output)
        return self.isomorphism(output)


if __name__ == "__main__":
    with open("public_key.json",'r') as f:
        G0, G1 = tuple(json.loads(f.read()))

    G0: Forest = Forest.from_dict(G0)
    G1: Forest = Forest.from_dict(G1)

    assert is_forest(G0)
    assert is_forest(G1)

    d = G0.map_to(G1)
    print(len(list(G0.trees())))
    assert d is not None
    print(d)
    assert G0.check_mapping(G1,d)

    r = remote(HOST,PORT)

    ROUNDS = 16
    generated = []

    for _ in range(ROUNDS):
        sigma = graph.random_isomorphism(G0)
        G2 = G0.map_vertices(sigma) #If we were using this correctly, this would be a random choice of G0 or G1. We're hacking, so we don't need to worry about that.
        generated.append((G2, sigma))
        r.sendline(G2.dumps().encode('utf-8'))

    challenges = r.recvline().strip().decode("utf-8")

    challenges = int.from_bytes(bytes.fromhex(challenges),'big')

    for G2, sigma in generated:
        challenge = challenges % 2

        if challenge == 1:
            tau = -d + sigma
        else:
            tau = sigma
        
        r.sendline(tau.dumps().encode('utf-8'))
        challenges >>= 1

    r.recvline()

    flag = r.recvline().strip()

    print(flag)