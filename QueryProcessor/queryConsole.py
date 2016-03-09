'''
The queryConsole is to read the query input, show query results and display error information

@author: minjian
'''

import psycopg2
import queryParser
import matGraphProcessor
import time
import os
from Tkinter import * #GUI package
from pylsy import pylsytable #for print table

#starts to execute the input query
def execQuery(conn, cur, executeCommand, result_Text):
    lowerCaseCommand = executeCommand.lower()
    
    #graph query contains rank, cluster and path operation
    if ("rank" in lowerCaseCommand) or ("cluster" in lowerCaseCommand)or ("path" in lowerCaseCommand):
        startTime = time.time()
        
        newExecuteCommand = queryParser.queryAnalyse(executeCommand, conn, cur)
        #newExecuteCommand = graphProcessor.queryAnalyse(executeCommand, conn, cur)
        #print "Total operation time is: ", (time.time() - startTime)
        #print newExecuteCommand  #for debug
        cur.execute(newExecuteCommand[:]) #remove the first space
        printResult(conn, cur, result_Text)
    
    #query about creating or dropping a materialised graph    
    elif ("create" in lowerCaseCommand or "drop" in lowerCaseCommand) and ("ungraph" in lowerCaseCommand or "digraph" in lowerCaseCommand):
        newExecuteCommand = matGraphProcessor.processCommand(executeCommand, conn, cur)
        eIndex = newExecuteCommand.index("view")
        cur.execute(newExecuteCommand[:]) #remove the first space
        conn.commit()
        #print newExecuteCommand[:eIndex] + "graph"
        result_Text.insert(INSERT, "Graph Operation Done")
        result_Text.config(state=DISABLED)
    
    #normal relational query without any graph functions
    else:
        #print executeCommand[:]
        cur.execute(executeCommand[:])  #remove the first space
        printResult(conn, cur, result_Text)

#prints results received from the database
def printResult(conn, cur, result_Text):
    print "Printing results"
    colnames = [desc[0] for desc in cur.description]
    table = pylsytable(colnames)
    rows = cur.fetchall()
    col_index = 0
    row_num = 0
    for i in rows:
        row_num += 1
        for each in i:
            print str(each) + '\t',
            table.append_data(colnames[col_index], str(each))
            col_index += 1
        print
        col_index = 0
        
        #solve the print problem of using pylsytable when the output data is too large
        if row_num == 100:  #every 100 lines, then we print a table, then create a new table
            result_Text.insert(INSERT, table)
            row_num = 0
            table = pylsytable(colnames)
    
    if row_num != 0:                   
        result_Text.insert(INSERT, table)
    conn.commit() 
    result_Text.config(state=DISABLED)    
     
'''code before use the pylsytable package   
    for each_name in colnames:
        #print "%-30s" % each_name.strip(),
        col_count = col_count + 1
        result_Text.insert(INSERT, "|%-10s" % each_name.strip())
    #print
    result_Text.insert(INSERT, '\n')
    
    while col_count > 0:
        result_Text.insert(INSERT, '+---------')
        col_count = col_count - 1
    
    result_Text.insert(INSERT, '\n')
    
    rows = cur.fetchall()
    for i in rows:
        for each in i:
            #print "%-30s" % str(each).strip(),
            result_Text.insert(INSERT, "|%-10s" % str(each).strip())
        #print
        result_Text.insert(INSERT, '\n')
    conn.commit() 
    result_Text.config(state=DISABLED)
'''
def start(query, result_Text):
    #starts the main function   
    homeDir = os.environ['HOME']
    memDir = "/dev/shm"
    
    if os.path.exists(homeDir + "/RG_Mat_Graph") == False:
        os.mkdir(homeDir + "/RG_Mat_Graph")
        
    if os.path.exists(memDir + "/RG_Tmp_Graph") == False:
        os.mkdir(memDir + "/RG_Tmp_Graph")    
           
    #Here is connect to your PostgreSQL
    #Change you database, user and port here
    #db = "acm_small"
    db = "acm"
    dbUser = "minjian"
    dbPort = 5432
    
    conn = psycopg2.connect(database=db, user=dbUser, port=dbPort)
    cur = conn.cursor()
    
    result_Text.config(state=NORMAL)
    start_time = time.time()
    try:
        execQuery(conn, cur, query, result_Text)
        #print "Total query time is: ", (time.time() - start_time)
        os.system("rm -fr /dev/shm/RG_Tmp_Graph/*")  #clear graphs on-the-fly
        queryParser.graphQueryAndResult.clear()  #clear parser's dictionary for result table names and graph sub-queries
    except psycopg2.ProgrammingError as reason:
        result_Text.insert(INSERT, str(reason))
        result_Text.config(state=DISABLED)
        #print str(reason)
    finally:
        cur.close()
        conn.close()
