#!/usr/bin/env python

#################################################
#   This code finds k-cores of a given graph    #
#   Author: Mojtaba (Omid) Rezvani              #
#################################################

import os
import sys
import commands
from os.path import isfile, join


# Our graph is a simple data structure: a list of edge lists, aka adjacency list
graph = []

# Let's read the graph from a file that has the list of edges. Note that the first
#   line does not include the number of vertics and edges
edge_list_file = sys.argv[1]
with open(edge_list_file) as edges:
    for line in edges:
        e = [int(v) for v in line.split()]
        if len(graph) < max(e[0], e[1]) + 1:
            for i in range(0, max(e[0], e[1]) + 1):
                graph.append([])
        graph[e[0]].append(e[1])
        graph[e[1]].append(e[0])
edges.close()

## kcore detection begins here
# Let's store the degrees of vertices
degrees = [None]*len(graph)
for i in range(0, len(graph)):
    degrees[i] = len(graph[i])

# Let k be the average degree
k = reduce(lambda x, y: x + y, degrees) / len(degrees)

# Initial set of vertices with degree less than k
q = [i for i in range(0, len(degrees)) if degrees[i] < k]
map(degrees.__setitem__, q, [-1]*len(q))

# Iterate over vertices and remove the ones with degree less than k
while len(q) > 0:
    # We pop the last item of the list, as it is done in O(1)
    v = q.pop(len(q) - 1)
    for u in graph[v]:
        degrees[u] -= 1
        if degrees[u] < k and degrees[u] != -1:
            q.append(u)
            degrees[u] = -1
    del graph[v][:]

# Find the connected components of the resulting graph
#   we here use degrees as a flag, in order to avoid space allocation
for i in range(0, len(graph)):
    degrees[i] = 0
components = [[]]
for i in range(0, len(graph)):
    components.append([])
    components[len(components) - 1].append(i)
    degrees[i] = 1
    qq = 0
    while qq < len(components[len(components) - 1]):
        v = components[len(components) - 1][qq]
        for u in graph[v]:
            if degrees[u] == 0:
                components[len(components) - 1].append(u)
                degrees[u] = 1
        qq += 1
