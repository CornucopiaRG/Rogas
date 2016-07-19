import os
import time
import snap

# Let's read the graph from a file that has the list of edges.
edge_list_file =os.environ['HOME'] + "/RG_Mat_Graph/coauthorship"
snap_Graph = snap.LoadEdgeList(snap.PUNGraph, edge_list_file, 0, 1)
start_time = time.time()

# Let k be the average degree
DegToCntV = snap.TIntPrV()
snap.GetDegCnt(snap_Graph, DegToCntV)
total_degree = 0
count_nodes = 0
for item in DegToCntV:
    total_degree += item.GetVal1() * item.GetVal2()
    count_nodes += item.GetVal2()
k = total_degree/count_nodes

# Start the KCore Algorithm
KCore = snap.GetKCore(snap_Graph, k)
if KCore.Empty():
    print 'No Core exists for K=%d' % k
else:
    print 'Core exists for K=%d' % k

#Save as Txt format    
snap.SaveEdgeList(KCore, 'mygraph.txt')

#Save as GraphViz format
#H = snap.TIntStrH()
#for each in KCore.Nodes():
   # H.AddDat(each.GetId(), "blue")
#snap.SaveGViz(KCore, "Graph1.dot", "Directed Random Graph", True, H)
