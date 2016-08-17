'''
The databaseInfoProcessor is to manage the database info, including realtion core and graphical view

@author: Yan Xiao
'''

import config
import StringIO 
from resultManager import QueryResult, TableResult
import helper
import snap

#two cases: relation core entire info and relation table info
def dealWithRelationCoreMetaInfo(cmd, isCore=True):
    infoString = helper.subprocessCmd(cmd)

    inputStream = StringIO.StringIO(infoString)
    relationCoreLines = inputStream.readlines()
    
    queryResult = QueryResult()
    if len(relationCoreLines) < 2:
        queryResult.setType("string")
        queryResult.setContent("Empty relation core information")
    else:
        queryResult.setType("table")
        #table header
        tableHeader = relationCoreLines[1]
        tableHeaderLst = [str(col).strip() for col in tableHeader.split('|')]
        #table content
        rowsContent = []
        endIndex = len(relationCoreLines)-2 if isCore else len(relationCoreLines)-1
        for index in xrange(3, endIndex):
            if relationCoreLines[index].strip() == "Indexes:":
                break
            oneRowContent = [str(col).strip() for col in relationCoreLines[index].split('|')]
            rowsContent.append(oneRowContent)

        queryResult.setContent(TableResult(tableHeaderLst, rowsContent))

    return queryResult

def getRelationCoreInfo():
    cmd = "psql -d " + config.DB + " -c '\d'"
    return dealWithRelationCoreMetaInfo(cmd, True)

def getRelationTableInfo(table_name):
    cmd = "psql -d " + config.DB + " -c '\d " + table_name + "'"
    return dealWithRelationCoreMetaInfo(cmd, False)

def getGraphicalViewInfo():
    from queryConsole import readTable
    queryResult = QueryResult()

    tableResult = readTable("my_matgraphs", "");
    if tableResult.total_num == 0:
        queryResult.setType("string")
        queryResult.setContent("Empty graphical view information")
    else:
        queryResult.setType("table")
        queryResult.setContent(tableResult)

    return queryResult

def getGraphicalGraphInfo(graph_name, conn, cur):
    queryResult = QueryResult()
    
    graph_name = graph_name.strip()
    graph_path = helper.getGraph(graph_name) 

    cur.execute("select graphType from my_matgraphs where matgraphname = '%s';" % (graph_name))
    conn.commit()
    one_row = cur.fetchone()
    if one_row is None:
        queryResult.setType("string") 
        queryResult.setContent("Can't find this graph in my_matgraphs") 
    else:
        graph_type = one_row[0].strip()
        snap_graph_type = snap.PNGraph if graph_type == "digraph" else snap.PUNGraph
        graph = snap.LoadEdgeList(snap_graph_type, graph_path, 0, 1)
        tmpGraphDir = "/dev/shm/RG_Tmp_Graph/"
        tmpGraphInfoPath = tmpGraphDir + graph_name + '_info'
        #snap print info
        snap.PrintInfo(graph, "Graph Type", tmpGraphInfoPath)

        tableHeaderLst = ['Attribute', 'Value']
        rowsContent = []
        with open(tmpGraphInfoPath) as f:
            for line in f:
                fields = line.split(':')
                key = fields[0].strip()
                value = fields[1].strip()
                if key == "Graph Type":
                    value = 'Directed' if graph_type == "digraph" else "Undirected"
                rowsContent.append([key, value])

        #definition
        cur.execute("select definition from pg_matviews where matviewname = '%s';" % (graph_name))
        conn.commit()
        one_row = cur.fetchone()
        if one_row is not None:
            rowsContent.append(['Definition', one_row[0].strip()])

        queryResult.setType("table")
        queryResult.setContent(TableResult(tableHeaderLst, rowsContent))

    return queryResult
