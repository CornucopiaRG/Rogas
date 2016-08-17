'''
The matGraphProcessor is to use materialized views to create materialized graphs.

@author: minjian
'''
import os
import helper
import subprocess
import clusterExecutor as cExe
import config

def getGraphCreationInfo(executeCommand):
    lowerCaseCommand = executeCommand.lower()
    startIndex = lowerCaseCommand.find("(") + 1
    commandWords = lowerCaseCommand[startIndex:].split()
    commandLength = len(commandWords)
    keyField = None 
    tableName = None
    for index in range(commandLength):
        command = commandWords[index].strip()
        if command == "select": 
            if keyField is None and index + 1 < commandLength:
                keyField = commandWords[index+1]
        elif command == "from":
            if tableName is None and index + 1 < commandLength:
                tableName = commandWords[index+1]

        if keyField is not None and tableName is not None:
            break
            
    keyField = helper.getAlphaNumSubString(keyField)
    dotIndex = keyField.find(".")
    keyField = keyField[dotIndex+1:]
    tableName = helper.getAlphaNumSubString(tableName)

    return keyField, tableName    

def generateEntityConnection(keyField, tableName):
    cmd = "psql -d " + config.DB + " -c '\d " + tableName + "'" 
    infoString = helper.subprocessCmd(cmd)
    infoString = infoString.lower()

    foreignKeyIndex = infoString.find('"' + tableName + '_' + keyField + '_fkey"')
    referencesIndex = infoString.find("references", foreignKeyIndex)
    leftBracketIndex = infoString.find("(", referencesIndex)
    rightBracketIndex = infoString.find(")", referencesIndex)

    entityTableName = infoString[referencesIndex + len("references"):leftBracketIndex].strip()
    entityIdField = infoString[leftBracketIndex+1:rightBracketIndex].strip()
    return entityIdField, entityTableName

def dropCreationInfo(graphName, conn, cur):
    cur.execute("delete from my_entity_connection where graphName = %s" % ("'" + graphName + "'"))
    conn.commit()

def analyseCreateInfo(executeCommand, graphName, graphType, conn, cur):
    keyField, tableName = getGraphCreationInfo(executeCommand)
    entityIdField, entityTableName = generateEntityConnection(keyField, tableName)

    cur.execute("select * from pg_tables where tablename = 'my_entity_connection';")
    rows = cur.fetchall()
    if len(rows) == 0:
        cur.execute("create table my_entity_connection (graphName text primary key, relationName text, keyField text);")
    conn.commit()

    cur.execute("insert into my_entity_connection values(%s, %s, %s)" % ("'" + graphName + "'", "'" + entityTableName + "'", "'" + entityIdField + "'"))
    conn.commit()

    from queryConsole import readTable
    tableResult = readTable(graphName, "")
    #write graph to file
    tmpGraphDir = "/dev/shm/RG_Tmp_Graph/"
    createGraphName = "crea_clu_" + graphName
    with open(tmpGraphDir + graphName, 'w') as f:
        for edge in tableResult.row_content:
            f.write(str(edge[0]) + '\t' + str(edge[1]) + os.linesep)

    #keep cluster result in database tmp table, which will be deleted automatically when cursor is closed
    clusterCommands = [graphName, 'MC', graphType, [], '', createGraphName]
    cExe.processCommand(clusterCommands, conn, cur, True)

#operates the my_matgraphs catalog and returns the rewritten query to PostgreSQL for execution
def processCommand(executeCommand, conn ,cur):
    lowerCaseCommand = executeCommand.lower()
    
    cur.execute("select * from pg_tables where tablename = 'my_matgraphs';")
    rows = cur.fetchall()
    
    #create the system catalog about materialised graphs
    if len(rows) == 0:
        cur.execute("create table my_matgraphs (matgraphname text primary key, graphType text);")
    conn.commit()
    
    if "create" in lowerCaseCommand: #create a materialized graph
        if "ungraph" in lowerCaseCommand:
            sIndex = lowerCaseCommand.index("ungraph")+len("ungraph")
            eIndex = lowerCaseCommand.index("as")
            graphName = lowerCaseCommand[sIndex:eIndex].strip()
            cur.execute("INSERT INTO my_matgraphs VALUES(%s, %s)" % ("'" + graphName + "'", "'ungraph'"))
            conn.commit()
            if executeCommand.find("ungraph") != -1:  
                return executeCommand.replace("ungraph", "materialized view"), graphName, "ungraph"
            elif executeCommand.find("UNGRAPH") != -1:
                return executeCommand.replace("UNGRAPH", "materialized view"), graphName, "ungraph"
            else:
                raise RuntimeError, "Graph type is not correct."
                
                     
        elif "digraph" in lowerCaseCommand:
            sIndex = lowerCaseCommand.index("digraph")+len("digraph")
            eIndex = lowerCaseCommand.index("as")
            graphName = lowerCaseCommand[sIndex:eIndex].strip()
            cur.execute("INSERT INTO my_matgraphs VALUES(%s, %s)" % ("'" + graphName + "'", "'digraph'"))
            conn.commit()
            if executeCommand.find("digraph") != -1:  
                return executeCommand.replace("digraph", "materialized view"), graphName, "digraph"
            elif executeCommand.find("DIGRAPH") != -1:
                return executeCommand.replace("DIGRAPH", "materialized view"), graphName, "digraph"
            else:
                raise RuntimeError, "Graph type is not correct."
        
    elif "drop" in lowerCaseCommand: #drop a materialized graph
            sIndex = lowerCaseCommand.index("graph")+len("graph")
            eIndex = lowerCaseCommand.index(";")
            graphName = lowerCaseCommand[sIndex:eIndex].strip() 
            cur.execute("DELETE FROM my_matgraphs where matgraphname = %s" % ("'" + graphName + "'"))
            conn.commit()
            if executeCommand.find("ungraph") != -1 or executeCommand.find("UNGRAPH") != -1:  
                return (executeCommand.replace("ungraph", "materialized view")).replace("UNGRAPH", "materialized view"), graphName, "ungraph"
            elif executeCommand.find("digraph") != -1 or executeCommand.find("DIGRAPH") != -1:  
                return (executeCommand.replace("digraph", "materialized view")).replace("DIGRAPH", "materialized view"), graphName, "digraph"
            else:
                raise RuntimeError, "Graph type is not correct." 
            graphPath = os.environ['HOME']  + "/RG_Mat_Graph/" + graphName
            os.system("rm -fr " + graphPath)
    
