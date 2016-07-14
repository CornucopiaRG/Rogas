"""
The new query parser for rogas. The parser parses a query sequentially and builds a tree for each query.

@Author: Chong Feng
"""

import re
import queryTree as tree


#Initialise a query tree and put the original query to the root of the tree
def queryTreeInitiation(query):
	preProcessedQuery = queryPreProcessing(query)
	root = tree.queryNode(preProcessedQuery)
	constructTree(root)
	return root

#Construct a tree by parsign queries on tree nodes recursively
def constructTree(node):
	if hasSubQuery(node.queryDict[node.queryID][0]):
		nodeParser(node)
		for eachChild in node.children:
			constructTree(eachChild)
	# else:
	# 	print "constructTree: ",node.query," does not have sub queries"


#Parse the query on a tree node
def nodeParser(node):	
	nodeQuery = node.queryDict[node.queryID][0]
	queryPosition = 0

	#Find graph operators or left parentheses
	subquery = re.search('([\s]+rank\(.*?\)(.*?as){0,1}|[\s]+cluster\(.*?\)(.*?as){0,1}|[\s]+path\(.*?\)(.*as\s\(.*\))|[\s]+\()',nodeQuery[queryPosition:])

	while (subquery != None):
		
			tempQuery = nodeQuery[queryPosition+subquery.start():queryPosition+subquery.end()].strip()
			#print "tempQuery: ", tempQuery
			if (tempQuery == "("):
				subQueryEndIndex = findLastRightBraket(nodeQuery,queryPosition+subquery.end()-1)

				# take out the first and the last brakets from the subquery
				query = nodeQuery[queryPosition+subquery.start():subQueryEndIndex].replace('(','',1)
				query = (query[:query.rfind(')')]+ query[query.rfind(')')+1:]).strip()

				subQueryID = node.add(query).queryID

				if (node.getNodeRewrittenQuery() == None):
					newOriginalQuery = node.getNodeOriginalQuery().replace(query,subQueryID)
				else:
					newOriginalQuery = node.getNodeRewrittenQuery().replace(query,subQueryID)
				
				node.addRewrittenQuery(newOriginalQuery)
				queryPosition = subQueryEndIndex


			else:
				if re.search("([\s]*rank\(.*?\)(.*?as))+|([\s]*cluster\(.*?\)(.*?as))+|[\s]+path\(.*?\)(.*as.\(.*\))",tempQuery) != None:
					subQueryEndIndex = findLastRightBraket(nodeQuery,queryPosition+subquery.end())
					
					# take out the first and the last brakets from the subquery
					subQuery = nodeQuery[queryPosition+subquery.start():subQueryEndIndex].strip()
					subQueryID = node.add(subQuery,"G").queryID 

					if (node.getNodeRewrittenQuery() == None):
						newOriginalQuery = node.getNodeOriginalQuery().replace(subQuery,subQueryID)
					else:
						newOriginalQuery = node.getNodeRewrittenQuery().replace(subQuery,subQueryID)

					#node.setNodeOriginalQuery(newOriginalQuery)
					node.addRewrittenQuery(newOriginalQuery)

				
					#print nodeQuery[queryPosition+subquery.start():subQueryEndIndex].strip()
					queryPosition = subQueryEndIndex
				else:
					subQueryID = node.add(tempQuery,"G").queryID
					
					if (node.getNodeRewrittenQuery() == None):
						newOriginalQuery=node.getNodeOriginalQuery().replace(tempQuery,subQueryID)
					else:
						newOriginalQuery=node.getNodeRewrittenQuery().replace(tempQuery,subQueryID)

					#node.setNodeOriginalQuery(newOriginalQuery)
					node.addRewrittenQuery(newOriginalQuery)

					queryPosition += subquery.end()
			
			subquery = re.search('([\s]+rank\(.*?\)(.*?as){0,1}|[\s]+cluster\(.*?\)(.*?as){0,1}|[\s]+path\(.*?\)(.*?as){0,1}|[\s]+\()',nodeQuery[queryPosition:])

			
#Check if a query in a node has sub-query
def hasSubQuery(query):
	if (re.search('([\s]+rank\(.*?\)(.*?as)*|[\s]+cluster\(.*?\)(.*?as)*|[\s]+path\(.*?\)|[\s]+\()',query) == None):
		return False
	else:
		return True

#Given a query string and a left parenthesis, find the corresponding right one
def findLastRightBraket(string,startingIndex):

	foundLastRightBracket =  False
	numberOfNested = 0
	cursorIndex = startingIndex


	while (foundLastRightBracket == False):
		if(string[cursorIndex] == '('):
			numberOfNested = numberOfNested + 1

		elif(string[cursorIndex] == ')'):
			numberOfNested = numberOfNested - 1
			if(numberOfNested == 0):
				foundLastRightBracket = True
	 	cursorIndex += 1
	 
	return cursorIndex


#Preprocess the query
def queryPreProcessing(query):
	preProcessedQuery = re.sub('\s+',' ',query.lower().replace("\n"," ")).strip()
	ori_query = re.sub('\s+',' ',query.replace("\n"," ")).strip()
	#print "====================" + preProcessedQuery
	#print "====================" + ori_query	
	#print
	
	flag = 1;
	end_index  = 0;
	for each in ori_query:
		if each == "'" :
			flag += 1
			if flag % 2 != 0:
				start_index = ori_query.index("'", end_index + 1)
				end_index = ori_query.index("'", start_index + 1)
				preProcessedQuery = preProcessedQuery.replace(preProcessedQuery[start_index + 1 : end_index], ori_query[start_index + 1 : end_index])
				#print ori_query[start_index + 1 : end_index]
	
	#print "=========after===========" + preProcessedQuery
	return preProcessedQuery
