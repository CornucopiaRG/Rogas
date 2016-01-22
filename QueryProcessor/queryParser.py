'''
The queryParser is to validate the graph sub-queries, analyse them and also rewrite them.
More details refer to the thesis "Towards a Unified Framework for Network Analytics" (the link to be published)

If the query has rank, cluster or path operations, then it sends rank, cluster or paths info 
to rankExecutor, clusterExecutor, pathExecutor respectively for executions.

@author: minjian
'''
import os
import rankExecutor as rExe
import clusterExecutor as cExe
import pathExecutor as pExe
import time
#this array is used to store each function and its related result table name
graphQueryAndResult = dict()

#Differentiates three types of graph sub-queries
def queryAnalyse(executeCommand, conn, cur):
    lowerCaseCommand = executeCommand.lower()
    commandList = executeCommand.split()
    commandList.reverse()  #so that inner sub-queries can be executed first
    
    #the operatorID corresponds to the order that graph operators occur in the query
    operatorID = 0
    
    indexMark = len(executeCommand)
    for each in commandList:
        if each.lower().startswith("rank("):
            operatorID += 1
            
            #avoid finding index like pagerank or other words that contain "rank"
            while lowerCaseCommand[lowerCaseCommand.rfind("rank",0, indexMark)-1] != ' ' or lowerCaseCommand[lowerCaseCommand.rfind("rank",0, indexMark)+4] != '(': 
                indexMark = lowerCaseCommand.rfind("rank",0, indexMark)
            
            graphIndex = lowerCaseCommand.rindex("rank",0, indexMark)
            indexMark = graphIndex
            rankCommands = getGQueryInfo(executeCommand, graphIndex, conn, cur)
            
            graphQuery = getGQuery(executeCommand, graphIndex, rankCommands[-1])
            #print "graphQuery ", graphQuery  #for debug
            
            #not run the same graph operation again
            if graphQuery not in graphQueryAndResult:
                resultTableName = "rank_" + rankCommands[0] + str(operatorID)
                rankCommands.append(resultTableName) #the last element is the result table name
                rExe.processCommand(rankCommands, conn, cur)
                graphQueryAndResult[graphQuery] = resultTableName
            #print "rankCommands ", rankCommands  #for debug
        
        if each.lower().startswith("cluster("):
            operatorID += 1
            
            #while lowerCaseCommand.rfind("clusterid",0, indexMark) == lowerCaseCommand.rfind("cluster",0, indexMark):
            #avoid finding index like clusterID or other words that contain "cluster"
            while lowerCaseCommand[lowerCaseCommand.rfind("cluster",0, indexMark)-1] != ' ' or lowerCaseCommand[lowerCaseCommand.rfind("cluster",0, indexMark)+7] != '(':  
                indexMark = lowerCaseCommand.rfind("cluster",0, indexMark)
                
            graphIndex = lowerCaseCommand.rindex("cluster",0, indexMark)
            indexMark = graphIndex
            clusterCommands = getGQueryInfo(executeCommand, graphIndex, conn, cur)
            
            graphQuery = getGQuery(executeCommand, graphIndex, clusterCommands[-1])
            #print "graphQuery ", graphQuery  #for debug
            
            #not run the same graph command again
            if graphQuery not in graphQueryAndResult:
                resultTableName = "cluster_" + clusterCommands[0] + str(operatorID) #the last element is tableName
                clusterCommands.append(resultTableName)
                cExe.processCommand(clusterCommands, conn, cur)
                graphQueryAndResult[graphQuery] = resultTableName
            #print "clusterCommands ", clusterCommands  #for debug
        
        if each.lower().startswith("path("):
            operatorID += 1
            
            #while (lowerCaseCommand.rfind("pathid",0, indexMark) == lowerCaseCommand.rfind("path",0, indexMark)) or (lowerCaseCommand.rfind("paths",0, indexMark) == lowerCaseCommand.rfind("path",0, indexMark)): 
            #avoid finding index like pathID or other words that contain "path"
            while lowerCaseCommand[lowerCaseCommand.rfind("path",0, indexMark)-1] != ' ' or lowerCaseCommand[lowerCaseCommand.rfind("path",0, indexMark)+4] != '(':  
                indexMark = lowerCaseCommand.rfind("path",0, indexMark)
            
            graphIndex = lowerCaseCommand.rindex("path",0, indexMark)
            indexMark = graphIndex + 4
            pathCommands = getGQueryInfo(executeCommand, graphIndex, conn, cur)
            
            graphQuery = getGQuery(executeCommand, graphIndex, pathCommands[-1])
            #print "graphQuery ", graphQuery  #for debug
            
            #not run the same graph command again
            if graphQuery not in graphQueryAndResult:
                resultTableName = "path_" + pathCommands[0] + str(operatorID) #the last element is tableName
                pathCommands.append(resultTableName)
                pExe.processCommand(pathCommands, conn, cur)
                graphQueryAndResult[graphQuery] = resultTableName
            #print "pathCommands ", pathCommands  #for debug
            
    #rewrite the query
    for eachStr in graphQueryAndResult.keys():
        executeCommand = executeCommand.replace(eachStr,graphQueryAndResult.get(eachStr))
    return executeCommand
    

#use a list to store graph info like src, des, type of graphs, measurements/algorithms used in the operation, the related table name
def getGQueryInfo(executeCommand, graphIndex, conn, cur):
    matGraphDir = os.environ['HOME'] + "/RG_Mat_Graph/"
    tmpGraphDir = "/dev/shm/RG_Tmp_Graph/"
    
    gQueryInfo = []  # [graphName, graphPara, graphType, commandArray]
    
    leftBracketIndex = executeCommand.index('(', graphIndex)
    rightBracketIndex = executeCommand.index(')', leftBracketIndex)
    graphCommand = (executeCommand[leftBracketIndex+1:rightBracketIndex]).split(',')
    
    graphName = graphCommand[0].strip()
    graphPara = graphCommand[1].strip()
    gQueryInfo.append(graphName)
    gQueryInfo.append(graphPara)
    
    whereClause = executeCommand[rightBracketIndex+1 :].strip()

    #query using a graph on-the-fly
    if whereClause.find(graphName,0,20) != -1:
        commandArray = getCoreCommands(whereClause, graphName, graphPara)
        graphInfo = commandArray[0]
        gQueryInfo.append(graphInfo[1]) #graph type
        
        if len(graphInfo) == 3:  #info about creating graph
            graphFile = open(tmpGraphDir + graphInfo[0], 'w')
            cur.execute(graphInfo[2] + ";")
            conn.commit()
            rows = cur.fetchall()
            startW_time = time.time()
            for i in rows:
                graphFile.write(str(i[0]) + '\t' + str(i[1]) + os.linesep)
            graphFile.close() 
            print "Graph writing time: ", time.time() - startW_time   
        else:
            raise RuntimeError, "Error about creating Graph on-the-fly!!"        
        
        gQueryInfo.append(commandArray)  
        
        #for debug    
        #for each in commandArray:
            #print "commandArray ", each
            
    #query using a materialized graph
    else:
        commandArray = getCoreCommands(whereClause, "null", graphPara)
        
        #for debug
        #for each in commandArray:
            #print "commandArray ", each
        #print "use views" 

        cur.execute("select * from pg_matviews where matviewname = '%s';" % (graphName))
        conn.commit()
        rows = cur.fetchall()
        if len(rows) == 1: #find the mat_graph
            cur.execute("select graphType from my_matgraphs where matgraphname = '%s';" % (graphName))
            conn.commit()
            myrow = cur.fetchone()
            gQueryInfo.append(myrow[0]) #get graph Type
            
            graphFile = open(matGraphDir + graphName, 'w')
            cur.execute("select * from %s;" % (graphName))
            conn.commit()
            rows = cur.fetchall()
            startW_time = time.time()
            for i in rows:
                graphFile.write(str(i[0]) + '\t' + str(i[1]) + os.linesep)
            graphFile.close()     
            print "Graph writing time: ", time.time() - startW_time 
            
            #print "find the view"
            gQueryInfo.append(commandArray)
            
        else:
            raise RuntimeError, "No such graph!!"
        
    return gQueryInfo
        
    
#Analyses the queries used to create graph on-the-fly or queries used to specify node condition        
def getCoreCommands(whereClause, graphName, graphPara):
    lowerWhereClause = whereClause.lower()
    
    commandArray = [] #elements are array  [graph:RGmapper, node:condition,...]
    
    #get info about the graph on-the-fly
    if graphName != "null":
        graphConstruct = [] #elements are string
        nameIndex = whereClause.index(graphName)
        isIndex = lowerWhereClause.index("is", nameIndex + len(graphName))
        asIndex = lowerWhereClause.index("as", isIndex + 2)
        graphType = whereClause[isIndex + 2 : asIndex].strip()
        graphConstruct.append(graphName)
        graphConstruct.append(graphType)
        graphConstruct.append(getSubQuery(whereClause, asIndex))
        commandArray.append(graphConstruct)
    
    #get info about the path expression
    if "/" in graphPara:
        nodes = graphPara.split("/")
        print nodes
        pointerIndex = 0
        for eachN in nodes:
            if eachN.isalnum():
                if eachN[0] != 'v' and eachN[0] != 'V':
                    raise RuntimeError, "Path Syntax Error!!"
                nodeConstruct = []
                foundNode = False
                while foundNode == False:
                    try:
                        pointerIndex = whereClause.index(eachN)
                    except ValueError :
                        raise RuntimeError, "Syntax Error!!"
                    if (whereClause[pointerIndex-1] == " " or whereClause[pointerIndex-1] == ",") and (whereClause[pointerIndex + len(eachN)] == " " or whereClause[pointerIndex + len(eachN)] == ","):
                        asIndex = lowerWhereClause.index("as", pointerIndex + len(eachN))
                        nodeConstruct.append(eachN)
                        nodeConstruct.append(getSubQuery(whereClause, asIndex))
                        foundNode = True
                        commandArray.append(nodeConstruct)
    return commandArray

#get the sub-query for creating graph on-the-fly and node condition
def getSubQuery(whereClause, asIndex):
    leftBracketIndexArray = []
    bracketIndexPair = []
    foundRGMapper = False    
    pointerIndex = asIndex + 2
    
    while foundRGMapper == False:
        pointerIndex += 1
        if whereClause[pointerIndex] == "(":
            leftBracketIndexArray.append(pointerIndex)
        
        if whereClause[pointerIndex] == ")":
            bracketIndexPair.append((leftBracketIndexArray.pop(),pointerIndex))
            if len(leftBracketIndexArray) == 0:
                foundRGMapper = True
    subQuery = whereClause[bracketIndexPair[-1][0] + 1 : bracketIndexPair[-1][1]].strip()
    return subQuery    

#return the whole graph sub-query
def getGQuery(executeCommand, graphIndex, commandArray):
    lowerCaseCommand = executeCommand.lower()
    
    queryEndIndex = 0
    if lowerCaseCommand[graphIndex] == "p":  #for path operations
        for eachQuery in commandArray:
            queryIndex = executeCommand.index(eachQuery[-1], graphIndex)
            if queryIndex > queryEndIndex:
                queryEndIndex = queryIndex + len(eachQuery[-1])
        lastBracketIndex = executeCommand.index(")", queryEndIndex)
        command = executeCommand[graphIndex : lastBracketIndex+1]
        return command
                
    elif lowerCaseCommand[graphIndex] == "r" or lowerCaseCommand[graphIndex] == "c": # for rank and cluster operations
        if len(commandArray) == 0:  #for materialized graph
            leftBracketIndex = executeCommand.index('(', graphIndex)
            rightBracketIndex = executeCommand.index(')', leftBracketIndex)
            command = executeCommand[graphIndex:rightBracketIndex+1]
            return command
        else:  #for graph on-the-fly
            queryEndIndex = executeCommand.index(commandArray[0][2], graphIndex) + len(commandArray[0][2])
            lastBracketIndex = executeCommand.index(")", queryEndIndex)
            command = executeCommand[graphIndex : lastBracketIndex+1]
            return command            
    