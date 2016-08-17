'''
The rankExecutor is to use SNAP and Graph-tool as algorithm support to run ranking operations.
After getting results from SNAP or Graph-tool, the rankExecutor will transform the results into a temp table in PostgreSQL

@author: minjian
'''
import snap
import time
import config
import graph_tool.all as gt
import numpy
import os

matGraphDir = os.environ['HOME'] + "/RG_Mat_Graph/"
tmpGraphDir = "/dev/shm/RG_Tmp_Graph/"

#graphCreator for graph=tool
class graphCreator():
    def __init__(self, graphTxtName, isDirected):
        f = open(graphTxtName)
        self.idIndexDict = dict()
        self.indexIdDict = dict()
        self.g = gt.Graph(directed= isDirected)
        index = 0
        edge_list = []
        for each in f:
            if each.startswith("#"):
                continue            
            strPair = each.strip().split()
            sourceId = int(strPair[0])
            targetId = int(strPair[1])
            if sourceId not in self.idIndexDict:   
                self.g.add_vertex()
                self.idIndexDict[sourceId] = index
                self.indexIdDict[index] = sourceId
                index += 1
            if targetId not in self.idIndexDict:
                self.g.add_vertex()
                self.idIndexDict[targetId] =  index
                self.indexIdDict[index] = targetId
                index += 1
                
            if ((sourceId, targetId) not in edge_list):
                if (isDirected == False):
                    edge_list.append((sourceId, targetId))
                    edge_list.append((targetId, sourceId))
                    self.g.add_edge(self.g.vertex(self.idIndexDict[sourceId]), self.g.vertex(self.idIndexDict[targetId]))
                else:
                    edge_list.append((sourceId, targetId))
                    self.g.add_edge(self.g.vertex(self.idIndexDict[sourceId]), self.g.vertex(self.idIndexDict[targetId]))
                    

#based on the measures, choose different methods to run the operations
def processCommand(rankCommands, conn ,cur):
    
    measureName = rankCommands[1].lower().strip()
        
    if "indegree" == measureName:
        Graph = snapCreateGraph(rankCommands)
        indegree(rankCommands, Graph, conn, cur)
        
    elif "outdegree" == measureName:
        Graph = snapCreateGraph(rankCommands)
        outdegree(rankCommands, Graph, conn, cur)
        
    elif "degree" == measureName:
        Graph = snapCreateGraph(rankCommands)
        degree(rankCommands, Graph, conn, cur)
        
    elif "pagerank" == measureName:
        Graph = snapCreateGraph(rankCommands)
        pageRank(rankCommands, Graph, conn, cur)
        
    elif "betweenness" == measureName:
        Graph = gtCreateGraph(rankCommands)
        betweenness(rankCommands, Graph, conn, cur)
        
    elif "closeness" == measureName:
        Graph = gtCreateGraph(rankCommands)
        closeness(rankCommands, Graph, conn, cur)


#create a graph using snap
def snapCreateGraph(rankCommands):
    graphPath = getGraph(rankCommands[0])
    #rankCommands[0] is the graph name
    if "digraph" == rankCommands[2].lower().strip():
        Graph = snap.LoadEdgeList(snap.PNGraph, graphPath, 0, 1)
        return Graph
        
    elif "ungraph" == rankCommands[2].lower().strip():
        Graph = snap.LoadEdgeList(snap.PUNGraph, graphPath, 0, 1)
        return Graph
    
#create a graph using graphTool   
def gtCreateGraph(rankCommands):
    graphPath = getGraph(rankCommands[0])
    #rankCommands[0] is the graph name
    if "digraph" in rankCommands[2].lower().strip():
        Graph = graphCreator(graphPath, True)
        return Graph
        
    elif "ungraph" in rankCommands[2].lower().strip():
        Graph = graphCreator(graphPath, False)
        return Graph    

#for indegree measure       
def indegree(rankCommands, Graph, conn, cur):
    InDegV = snap.TIntPrV()
    before_time = time.time()
    snap.GetNodeInDegV(Graph, InDegV)
    print "Total handling time is: ", (time.time() - before_time)
    DegH = snap.TIntIntH()
    slist = sortNodes(InDegV, DegH)
    createTable(rankCommands, slist, DegH, conn, cur)

#for outdegree measure      
def outdegree(rankCommands, Graph, conn, cur):
    OutDegV = snap.TIntPrV()
    before_time = time.time()
    snap.GetNodeOutDegV(Graph, OutDegV)
    print "Total handling time is: ", (time.time() - before_time)
    DegH = snap.TIntIntH()
    slist = sortNodes(OutDegV, DegH)
    createTable(rankCommands, slist, DegH, conn, cur)

#for betweenness measure
def degree(rankCommands, Graph, conn, cur):
    DegreeH = snap.TIntFltH()
    before_time = time.time()
    for NI in Graph.Nodes():
        DegreeH[NI.GetId()] = snap.GetDegreeCentr(Graph, NI.GetId())
    print "Total handling time is: ", (time.time() - before_time)
    slist = sorted(DegreeH, key = lambda key : DegreeH[key], reverse = True)
    createTable(rankCommands, slist, DegreeH, conn, cur)

#for pageRank measure
def pageRank(rankCommands, Graph, conn, cur):
    PRankH = snap.TIntFltH()
    before_time = time.time()
    snap.GetPageRank(Graph, PRankH)
    print "Total handling time is: ", (time.time() - before_time)
    slist = sorted(PRankH, key = lambda key : PRankH[key], reverse = True)
    createTable(rankCommands, slist, PRankH, conn, cur)

#for betweenness measure
def betweenness(rankCommands, Graph, conn, cur):
    if config.IS_GRAPH_TOOL_OPENMP:
        gt.openmp_set_num_threads(4) #enable 4 threads for runing algorithm
    before_time = time.time()
    vp = gt.betweenness(Graph.g)[0] #betweenness returns two property map (vertex map and edge map) [0] means use vertex map
    values = vp.get_array()
    idBt = dict()
    for each in Graph.g.vertices():
        idBt[Graph.indexIdDict[each]] = values[each]
    print "Total handling time is: ", (time.time() - before_time)
    slist = sorted(idBt, key = lambda key: idBt[key], reverse = True)
    createTable(rankCommands, slist, idBt, conn, cur)
    
#for closeness measure
def closeness(rankCommands, Graph, conn, cur):
    if config.IS_GRAPH_TOOL_OPENMP:
        gt.openmp_set_num_threads(4) #enable 4 threads for runing algorithm
    before_time = time.time()
    c = gt.closeness(Graph.g) 
    values = c.get_array()
    idCl = dict()
    for each in Graph.g.vertices():
        if numpy.isnan(values[each]):
            idCl[Graph.indexIdDict[each]] = 0.0
        else:   
            idCl[Graph.indexIdDict[each]] = values[each]
    print "Total handling time is: ", (time.time() - before_time)
    slist = sorted(idCl, key = lambda key: idCl[key], reverse = True)
    createTable(rankCommands, slist, idCl, conn, cur)
    #printRankResult(slist, idCl)

#based on the measure outcome, sort the result (only for indegree and outdegree)
def sortNodes(DegV, DegH):    
    #Transfer into Hash Table so that we can use sorted method.
    for item in DegV:
        DegH[item.GetVal1()] = item.GetVal2()
    slist = sorted(DegH, key = lambda key: DegH[key], reverse = True)
    return slist

#get the graph from materialised graph dir or tmp graph dir
def getGraph(graphName):
    matGraphDir = os.environ['HOME'] + "/RG_Mat_Graph/"
    tmpGraphDir = "/dev/shm/RG_Tmp_Graph/"
    
    if os.path.exists(tmpGraphDir + graphName):
        return tmpGraphDir + graphName
    elif os.path.exists(matGraphDir + graphName):
        return matGraphDir + graphName
    else:
        raise RuntimeError, "No such graph!!"

#create temp table in the PostgreSQL.    
def createTable(rankCommands, slist, DegH, conn, cur):
    tableName = rankCommands[-1]
    #print "create temp table " + graphCommand[3] + " (" + graphCommand[1] + " int not null primary key, " + graphCommand[2] + " int);"
    #print "create temp table " + tableName + " (" + Col1 + " int not null primary key, " + Col2 + " real);"
    cur.execute("create temp table " + tableName + " ( VertexID int not null primary key,  Value real);")
    conn.commit()
    for item in slist:
        cur.execute("INSERT INTO " + tableName + " VALUES(%s, %s)" % (item, DegH[item]))
        conn.commit()
