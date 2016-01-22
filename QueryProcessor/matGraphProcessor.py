'''
The matGraphProcessor is to use materialized views to create materialized graphs.

@author: minjian
'''
import os
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
                return executeCommand.replace("ungraph", "materialized view")
            elif executeCommand.find("UNGRAPH") != -1:
                return executeCommand.replace("UNGRAPH", "materialized view")
            else:
                raise RuntimeError, "Graph type is not correct."
                
                     
        elif "digraph" in lowerCaseCommand:
            sIndex = lowerCaseCommand.index("digraph")+len("digraph")
            eIndex = lowerCaseCommand.index("as")
            graphName = lowerCaseCommand[sIndex:eIndex].strip()
            cur.execute("INSERT INTO my_matgraphs VALUES(%s, %s)" % ("'" + graphName + "'", "'digraph'"))
            conn.commit()
            if executeCommand.find("digraph") != -1:  
                return executeCommand.replace("digraph", "materialized view")
            elif executeCommand.find("DIGRAPH") != -1:
                return executeCommand.replace("DIGRAPH", "materialized view")
            else:
                raise RuntimeError, "Graph type is not correct."
        
    elif "drop" in lowerCaseCommand: #drop a materialized graph
            sIndex = lowerCaseCommand.index("graph")+len("graph")
            eIndex = lowerCaseCommand.index(";")
            graphName = lowerCaseCommand[sIndex:eIndex].strip() 
            cur.execute("DELETE FROM my_matgraphs where matgraphname = %s" % ("'" + graphName + "'"))
            conn.commit()
            if executeCommand.find("ungraph") != -1 or executeCommand.find("UNGRAPH") != -1:  
                return (executeCommand.replace("ungraph", "materialized view")).replace("UNGRAPH", "materialized view")
            elif executeCommand.find("digraph") != -1 or executeCommand.find("DIGRAPH") != -1:  
                return (executeCommand.replace("digraph", "materialized view")).replace("DIGRAPH", "materialized view")
            else:
                raise RuntimeError, "Graph type is not correct." 
            graphPath = os.environ['HOME']  + "/RG_Mat_Graph/" + graphName
            os.system("rm -fr " + graphPath)
    