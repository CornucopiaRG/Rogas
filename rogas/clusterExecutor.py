'''
The clusterExecutor is to use SNAP and Graph-tool as algorithm support to run clustering operations.
After getting results from SNAP or Graph-tool, the clusterExecutor will transform the results into a temp table in PostgreSQL

@author: minjian
'''
import snap
import time
import os
import config
import graph_tool.all as gt

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
                    
#based on the algorithms, choose different methods to run the operations
def processCommand(clusterCommands, conn, cur, isTempTable=True):
    graphPath = getGraph(clusterCommands[0])
    algorithmName = clusterCommands[1].lower().strip()
    
    #Determine measurement   
    if "gn" == algorithmName:
        if "ungraph" == clusterCommands[2].lower().strip():
            Graph = snap.LoadEdgeList(snap.PUNGraph, graphPath, 0, 1)
            
        else:
            raise RuntimeError, "Grapy Type Error: GN algorithm only support ungraph!"  
        print "Start Algorithm"          
        comDetect("gn", clusterCommands, Graph, conn, cur)
        
    elif "cnm" == algorithmName:
        if "ungraph" == clusterCommands[2].lower().strip():
            Graph = snap.LoadEdgeList(snap.PUNGraph, graphPath, 0, 1)
            
        else:
            raise RuntimeError, "Grapy Type Error: CNM algorithm only support ungraph!" 
        print "Start Algorithm"         
        comDetect("cnm", clusterCommands, Graph, conn, cur)
        
    elif "cc" == algorithmName:
        Graph = snapCreateGraph(clusterCommands)
        print "Start Algorithm"  
        connectedComponent(clusterCommands, Graph, conn, cur)
        
    elif "scc" == algorithmName:
        Graph = snapCreateGraph(clusterCommands)
        print "Start Algorithm"  
        strongConnectedComponent(clusterCommands, Graph, conn, cur)
        
    elif "mc" == algorithmName:
        Graph = gtCreateGraph(clusterCommands)
        print "Start Algorithm"  
        blockModel(clusterCommands, Graph, conn, cur, isTempTable)
        
#create a graph using snap
def snapCreateGraph(clusterCommands):
    graphPath = getGraph(clusterCommands[0])
    if "digraph" in clusterCommands[2].lower().strip():
        Graph = snap.LoadEdgeList(snap.PNGraph, graphPath, 0, 1)
        return Graph
        
    elif "ungraph" in clusterCommands[2].lower().strip():
        Graph = snap.LoadEdgeList(snap.PUNGraph, graphPath, 0, 1)
        return Graph
    
#create a graph using graphTool   
def gtCreateGraph(clusterCommands):
    graphPath = getGraph(clusterCommands[0])
    if "digraph" in clusterCommands[2].lower().strip():
        Graph = graphCreator(graphPath, True)
        return Graph
        
    elif "ungraph" in clusterCommands[2].lower().strip():
        Graph = graphCreator(graphPath, False)
        return Graph 
    
#using snap to implement the community detection algorithm (GN or CNM) 
def comDetect(algorithm, clusterCommands, Graph, conn, cur):
    CmtyV = snap.TCnComV()
    before_time = time.time()
    if algorithm == "gn":
        modularity = snap.CommunityGirvanNewman(Graph, CmtyV)
    if algorithm == 'cnm':
        modularity = snap.CommunityCNM(Graph, CmtyV)
    print "Total handling time is: ", (time.time() - before_time)
    createTable(clusterCommands, CmtyV, conn, cur)
    print "The modularity of the network is %f" % modularity       

#find connected components
def connectedComponent(clusterCommands, Graph, conn, cur):
    Components = snap.TCnComV()
    snap.GetWccs(Graph, Components)
    createTable(clusterCommands, Components, conn, cur)

#find strongly connected components    
def strongConnectedComponent(clusterCommands, Graph, conn, cur):
    Components = snap.TCnComV()
    snap.GetSccs(Graph, Components)
    createTable(clusterCommands, Components, conn, cur)
    #printClusterResult(Components) 

#using Graph-tool to implement the MC community detection algorithm
def blockModel(clusterCommands, Graph, conn, cur, isTempTable):
    if config.IS_GRAPH_TOOL_OPENMP:
        gt.openmp_set_num_threads(4) #enable 4 threads for runing algorithm
    g = Graph.g
    state = gt.minimize_blockmodel_dl(g)
    b = state.b
    values = b.get_array()
    maxCommID = sorted(values[:])[-1]
    commDict = []
    for i in range(maxCommID+1):
        commDict.append([])
    index = 0
    for each in values:
        nodeID = Graph.indexIdDict[index]
        commDict[each].append(nodeID)
        index += 1
    createTable(clusterCommands, commDict, conn, cur, isTempTable)

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
def createTable(clusterCommands, CmtyV, conn, cur, isTempTable=True):
    tableName = clusterCommands[-1]
    Col1= "ClusterID"
    Col2= "Size"
    Col3= "Members"
    
    #print "create temp table " + tableName + " (" + Col1 + " int not null primary key, " + Col2 + " int[]);"
    create_table_sql = "create "
    if isTempTable:
        create_table_sql += "temp " 
    create_table_sql += "table " + tableName + " (" + Col1 + " int not null primary key, " + Col2 + " int, " + Col3 + " int[]);"
    cur.execute(create_table_sql)
    conn.commit()
    
    communityId = 0
    for Cmty in CmtyV:
        communityId += 1
        membersId = ""
        size = len(Cmty)
        for NI in Cmty:
            membersId += str(NI) + ","
            
        cur.execute("INSERT INTO " + tableName + " VALUES(%s, %s, %s)" % (communityId, size,"'{" + membersId[:-1] + "}'"))
        conn.commit()
