'''
The queryOptimiser class can help save and retrieve execution result of a query. It can also 
save and retrieve exuecution result table name of a graph sub-query. 

@author: Chong Feng
'''


import re

queryDict = dict(); #The variable that stores the hash value of a query and it execution result 

graphQueryAndResult = dict(); #The variable that stores tree patterns and their execution result table names

#Check if a query's hash value is existed in the cache
def checkQueryDictHVal(query):
	cleanedQuery = queryPreProcess(query)
	queryHashVal = hash(cleanedQuery)
	if (queryDict.has_key(queryHashVal) == True):
		print ("--------------------------------------------------------------")
		print ("\nOptimiser: queryDict has this whole query")
		return True
	else:
		print ("--------------------------------------------------------------")
		print ("\nOptimiser: queryDict does not have this whole query")
		return False

#Get the complete execution result of a query 
def getQueryDictValue(query):
	cleanedQuery = queryPreProcess(query)
	queryHashVal = hash(cleanedQuery)	
	return queryDict[queryHashVal]

#Save a query and its execution result in cache
def setQueryDictValue(query,result):
	cleanedQuery = queryPreProcess(query)
	queryHashVal = hash(cleanedQuery)	
	queryDict[queryHashVal] = result


#Check if a graph sub-query exists in the cache.
def checkGraphQueryAndResult(graphQuery):
	cleanedGraphQuery = queryPreProcess(graphQuery)
	if(graphQueryAndResult.has_key(cleanedGraphQuery)):
		print ("\nOptimiser: graphQueryAndResult has this query")
		return True
	else:
		print ("\nOptimiser: graphQueryAndResult does not have this query")
		return False

#Set a graph sub-query and its execution result table name into the cahce
def setGraphQueryAndResult(graphQuery,resultTableName):
	#cleanedGraphQuery = queryPreProcess(graphQuery)
	graphQueryAndResult[graphQuery] = resultTableName

#Get the execution result table name of a graph sub-query
def getGraphQueryAndResult(graphQuery):
	#cleanedGraphQuery = queryPreProcess(graphQuery)
	return graphQueryAndResult[graphQuery] 

#Preprocess queries
def queryPreProcess(query):
	preProcessedQuery = re.sub('\s+',' ',query.lower().replace("\n"," ")).strip()	
	return preProcessedQuery






