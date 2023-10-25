# Graph Isomorophism ZKP: Forest for the Trees
This is a graph-isomorphism based zero knowledge proof scheme. The protocol itself is secure, but the key generation creates a forest rather than a random graph. This makes it possible to solve the graph isomorphism problem directly, using the algorithm implemented in soln.py.

# Challenge files
graph.py, gen_key.py, server.py are the only files required. Note that this graph.py is **not** the same as in the other graph-based problem. It has a few new features desigend to make the isomorphism algorithm easier to implement.

# Challenge Descritpion
I've revised my graph-based zero knowledge proof scheme. I think I have the basic protocol down now. Did I mess anything else up?