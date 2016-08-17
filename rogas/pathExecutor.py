'''
The pathExecutor is to use NetworkX as algorithm support to run path finding operations.
After getting results from NetworkX, the pathExecutor will transform the results into a temp table in PostgreSQL

@author: minjian
'''
import networkx as nx
import os
import queryParser

def nodesInShortestPath(graph, start_node, end_node):
    try:
        #V1//V2#
        pathList = findPaths(graph, start_node, end_node, 0)
    except (nx.exception.NetworkXError, nx.exception.NetworkXNoPath, KeyError) as reasons:
        pathList = []

    return pathList[0] if len(pathList) > 0 else []

#based on the path expression, choose different methods to run the operations
def processCommand(pathCommands, conn ,cur, graphQueryAndResult):
    
    #createGraph
    graphPath = getGraph(pathCommands[0])
    if "digraph" == pathCommands[2].strip():
        Graph = createGraph(graphPath, "digraph")
        
    elif "ungraph" == pathCommands[2].strip():
        Graph = createGraph(graphPath, "ungraph")
    
        
    #differentiate V1//V2 and V1/./V2
    paths = analysePathSymbol(pathCommands[1])
    pathLenList = []
    for each in paths:
        if (str(each)).find('//') != -1:
            pathLen = 0
            pathLenList.append(pathLen)
        else:
            pathLen = int((str(each)).count('/'))
            pathLenList.append(pathLen)
    
    #find all the members for one column
    columnList = []
    for eachCommand in pathCommands[3]:  #the fourth element of pathCommands is commandArray
        if len(eachCommand) == 2:  #means the node condition, otherwise it is a query for create graphs
            nodeCommand = eachCommand[1].replace(' ', ' distinct ', 1)  #a column only contains unique value
            #print nodeCommand
            if ("rank" in nodeCommand) or ("cluster" in nodeCommand):
                for eachStr in graphQueryAndResult.keys():
                    nodeCommand = nodeCommand.replace(eachStr, graphQueryAndResult.get(eachStr))
            cur.execute(nodeCommand)
            
            rows = cur.fetchall()
            #print rows
            conn.commit()   
            columnList.append(rows)           
    
    #without middle node condition
    if len(paths) == 1:
        srcCols = columnList[0]
        desCols = columnList[1]
        print "start to create table"
        createTable(pathCommands, Graph, srcCols, desCols, pathLenList[0], conn, cur)
    #with middle node conditions (S\.\.\N\.\D or S\..\N\..\D)
    else:
        print "start to create Mtable"
        createMTable(pathCommands, Graph, columnList, pathLenList, conn, cur) 

#Create graphs in NetworkX    
def createGraph(graphTxtName, graphType):
    if graphType == "digraph":
        Graph = nx.DiGraph()
    elif graphType == "ungraph":
        Graph = nx.Graph()
        
    #Create Graph
    f = open(graphTxtName)
    edgeList = []
    for eachLine in f:
        s = int((eachLine.split())[0])
        d = int((eachLine.split())[1])
        t = s, d #print t
        edgeList.append(t)
        
    Graph.add_edges_from(edgeList)
    print "number of nodes: ", Graph.number_of_nodes()
    print "number of edges: ", Graph.number_of_edges()
    return Graph
            
#for example: dealing with V1/./V2/./V3, separate it into two paths.            
def analysePathSymbol(pathSymbol):
    paths = []
    i = 0
    nodes = [e for e in pathSymbol.split("/") if e != '.' and e!= '']
    
    while i + 1 < len(nodes):
        sIndex = pathSymbol.index(nodes[i])
        eIndex = pathSymbol.index(nodes[i+1])
        paths.append(pathSymbol[sIndex:eIndex+len(nodes[i+1])])
        i += 1
    #for debug    
    #print paths
    return paths

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

#create temp table in the relational DB to store the results (without middle node condition, e.g. V1/././V2)        
def createTable(pathCommands, Graph, srcRows, desRows, pathLen, conn, cur):
    tableName = pathCommands[-1]
    Col1 = "PathId"
    Col2 = "Length"
    Col3 = "Paths"
        
    #print "create temp table " + graphCommand[3] + " (" + graphCommand[1] + " int not null primary key, " + graphCommand[2] + " int);"
    cur.execute("create temp table " + tableName + " (" + Col1 + " int not null primary key, " + Col2 + " int , " + Col3 + " integer[] );")
    conn.commit()
    
    pathId = 0
    for i in range(0,len(srcRows)):
        for j in range(0, len(desRows)):
            if (srcRows[i][0] != desRows[j][0]):
                #print "enter path1"
                try:
                    pathList = findPaths(Graph, srcRows[i][0], desRows[j][0], pathLen)
                except (nx.exception.NetworkXError, nx.exception.NetworkXNoPath, KeyError) as reasons:
                    #print reasons
                    continue
                for path in pathList:
                    pathId += 1
                    #print path, len(path)-1
                    cur.execute("INSERT INTO " + tableName + " VALUES(%s, %s, array %s)" % (pathId, len(path)-1, path))
                    #cur.execute("UPDATE " + tableName + " SET %s = %s || ARRAY[1,2,3,4] WHERE %s = %s" % (Col3, Col3, Col1, pathId))
                    conn.commit()
    print "complete the paths temp table"  

#create temp table in the relational DB to store the results (with middle node conditions, e.g. V1/.V2/.V3)        
def createMTable(pathCommands, Graph, columnList, pathLenList, conn, cur):
    '''
    for debug
    for each in rowsList:
        print each
    for each in pathLenList:
        print each
    print "enter MTable"
    '''
    tableName = pathCommands[-1]
    Col1 = "PathId"
    Col2 = "Length"
    Col3 = "Path"
        
    #print "create temp table " + graphCommand[3] + " (" + graphCommand[1] + " int not null primary key, " + graphCommand[2] + " int);"
    cur.execute("create temp table " + tableName + " (" + Col1 + " int not null primary key, " + Col2 + " int , " + Col3 + " integer[] );")
    conn.commit()
    
    pathId = 0
    srcCols = columnList[-1]
    desCols = columnList[-2]
    pathLen = pathLenList[0]
    
    for i in range(0,len(srcCols)):
        for j in range(0, len(desCols)):
            if (srcCols[i][0] != desCols[j][0]):
                #print "enter path1"
                try:
                    pathList = findPaths(Graph, srcCols[i][0], desCols[j][0], pathLen)
                except (nx.exception.NetworkXError, nx.exception.NetworkXNoPath, KeyError) as reasons:
                    #print reasons
                    continue
                tempPathList = []
                #this is the first path e.g. V1/./V2 
                for path in pathList:
                    #Here starts the next several paths
                    for pl in range(1, len(pathLenList)):
                        sCols = columnList[-pl-1]
                        dCols = columnList[-pl-2]
                        
                        #Here is for the last path e.g. V2/./V3
                        #only for the last path, we start to insert values into table
                        if pl == len(pathLenList) - 1:
                            for a in range(0, len(sCols)):
                                for b in range(0, len(dCols)):
                                    #make sure the first node not equals to the last node
                                    if (srcCols[i][0] != dCols[b][0]) and (sCols[a][0] != dCols[b][0]):
                                        try:
                                            lastPathList = findPaths(Graph, sCols[a][0], dCols[b][0], pathLenList[pl])
                                        except (nx.exception.NetworkXError, nx.exception.NetworkXNoPath, KeyError) as reasons:
                                            #print reasons  
                                            continue                                       
                                        #print "enter update:", pathId
                                        if len(tempPathList) == 0:
                                            for lastPath in lastPathList:
                                                pathId += 1
                                                cpPath = path[:]
                                                cpPath.extend(lastPath[1:])
                                                cur.execute("INSERT INTO " + tableName + " VALUES(%s, %s, array %s)" % (pathId, len(cpPath)-1, cpPath))
                                                #cur.execute("UPDATE " + tableName + " SET %s = %s || ARRAY%s WHERE %s = %s" % (Col3, Col3, path[1:], Col1, pathId))
                                                #cur.execute("UPDATE " + tableName + " SET %s = %s + %s WHERE %s = %s" % (Col2, Col2, pathLenList[pl], Col1, pathId))
                                                conn.commit()
                                        else:
                                            for each in tempPathList:
                                                for lastPath in lastPathList:
                                                    pathId += 1
                                                    cpPath = each[:]
                                                    cpPath.extend(lastPath[1:])
                                                    cur.execute("INSERT INTO " + tableName + " VALUES(%s, %s, array %s)" % (pathId, len(cpPath)-1, cpPath))
                                                    conn.commit()
                        
                        #Here is the paths between first path and last path
                        #We only expand the result list and store the new results into a tempPathList
                        else:
                            for a in range(0, len(sCols)):
                                for b in range(0, len(dCols)):
                                    #the source and the des must be different
                                    if (sCols[a][0] != dCols[b][0]):
                                        try:
                                            conPathList = findPaths(Graph, sCols[a][0], dCols[b][0], pathLenList[pl]) 
                                        except (nx.exception.NetworkXError, nx.exception.NetworkXNoPath, KeyError) as reasons:
                                            #print reasons
                                            continue                                          
                                        if len(tempPathList) == 0:
                                            for conPath in conPathList:
                                                cpPath = path[:]
                                                cpPath.extend(conPath[1:])
                                                tempPathList.append(cpPath)
                                        else:
                                            cpTempPathList = tempPathList[:]
                                            for each in tempPathList:
                                                tempPathList.remove(each)
                                            for each in cpTempPathList:
                                                for conPath in conPathList:
                                                    cpPath = each[:]
                                                    cpPath.extend(conPath[1:])
                                                    tempPathList.append(cpPath)
    print "complete the paths temp Mtable"  


#use networkx to find paths    
def findPaths(Graph, source, des, pathLen):
    #for path like V1//V2
    if pathLen == 0:
        #Old version find paths:
        #while True:
            #pathLen += 1
            #print source, des
            #paths = nx.all_simple_paths(Graph, source, des, pathLen)
            #if (len(pathList) != 0) or (pathLen == 3) :
            #if (pathLen == 3) :
                #pathLen = 0
                #break  
            #New version find paths:
        paths = nx.all_shortest_paths(Graph, source, des)
        pathList = list(paths)
        return pathList
    
    #for path like V1/./V2 with specific length
    else:
        paths = nx.all_simple_paths(Graph, source, des, pathLen)
        pathList = list(paths)
        return pathList
