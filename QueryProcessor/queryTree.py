'''
Tree Structure to store query tree.
@author: Chong Feng
'''

import queryParser
import queryOptimiser

class queryNode:
	def __init__(self,queryData,nodeID=None, queryType=None):
		self.children = []
		self.query = queryData
		self.parent = None

		#queryDict has the structure: {queryID:[graph type,original query, original query replaced by queryID query]}
		self.queryDict = dict()
		if nodeID == None:
			self.queryID = "0"
		else:
			self.queryID = nodeID

		if queryType == None:
			self.queryType = "R"
		else:
			self.queryType = queryType

		self.queryDict[self.queryID] = [None]*2
		self.queryDict[self.queryID][0] = queryData


	def getNodeID(self):
		return self.queryID

	def getNodeType(self):
		return self.queryType

	def getNodeOriginalQuery(self):
		return self.queryDict[self.queryID][0]

	def setNodeOriginalQuery(self, query):
		self.queryDict[self.queryID][0] = query

	def getNodeRewrittenQuery(self):
		return self.queryDict[self.queryID][1]

	def addRewrittenQuery(self,rewrittenQuery):
		self.queryDict[self.queryID][1] = rewrittenQuery


	#Add a query as a child node to a node
	def add(self,queryData,queryType = None):
		queryID = self.queryID+str((len(self.children)))
		if queryType == None:
			tempNode = queryNode(queryData,queryID)
		else:
			tempNode = queryNode(queryData,queryID,queryType)

		tempNode.parent = self

		self.children.append(tempNode)

		return tempNode

	# #Add a node to a node 
	# def addNode(self,node):
	# 	node.parent = self
	# 	node.queryID = self.queryID+str((len(self.children)-1))
	# 	self.children.append(node)
	# 	return node
	
	# def addToNodeQuery(self, query):
	# 	self.query = self.query + " " + query
	# 	self.query.strip()
	# 	return self.query
  
	def getNodeByIndex(self,index):
		return self.children[index] 

	def getNodeByName(self,nodeName):
	 	for child in self.children:
	 		if(child.query == nodeName):
	 			return child
	 	return -1;

	def treeMatch(self, node2):
		match = True
		selfChildrenNameList = []		

		for eachSelfChild in self.children:
			selfChildrenNameList.append(eachSelfChild.query)
		
		if(self.query == node2.query):	
			if(len(node2.children)!=0):
				for eachNode2Child in node2.children:
					if eachNode2Child.query in selfChildrenNameList:
						return True & self.getNodeByName(eachNode2Child.query).treeMatch(eachNode2Child)
					else:
						return False
			else:
				return True
		else:
			for eachSelfChild in self.children:
				eachSelfChild.treeMatch(node2)


	#Print the structure of a tree
	def printNode(self):
		childrenList = []
		for eachChild in self.children:
			childrenList.append(eachChild.query)
		print "ID: ", self.queryID, "queryType: ", self.queryType, " Node query 0: ",self.queryDict[self.queryID][0], " Node query 1: ", self.queryDict[self.queryID][1]
		print "\n"
		for eachChild in self.children:
			eachChild.printNode()


	#Traverse a tree in post order, and call execution functions when a graph node is found.
	def postOrder(self,conn,cur):
		for eachChild in self.children:
			eachChild.postOrder(conn,cur)
		if(self.getNodeType() == "G"):

			if(queryOptimiser.checkGraphQueryAndResult(self.getNodeOriginalQuery())==False):
				resultTableName = queryParser.queryExecutor(self,conn,cur)
				queryOptimiser.setGraphQueryAndResult(self.getNodeOriginalQuery(),resultTableName)

				#Replace the node ID in the parent query with the execution table name
				if(self.parent != None):
					self.parent.addRewrittenQuery(self.parent.getNodeRewrittenQuery().replace(self.queryID,resultTableName))
					parent = self.parent
					
					while(parent.parent!= None):
						parent.parent.addRewrittenQuery(parent.parent.getNodeRewrittenQuery().replace(parent.queryID,parent.getNodeRewrittenQuery()))
						parent = parent.parent

			else:
				print "In postOrder: cache hit!"
				#Replace the node ID in the parent query with the execution table name
				if(self.parent != None):
					cachedTableName = queryOptimiser.getGraphQueryAndResult(self.getNodeOriginalQuery())
					self.parent.addRewrittenQuery(self.parent.getNodeRewrittenQuery().replace(self.queryID,cachedTableName))

					parent = self.parent
					
					while(parent.parent!= None):
						parent.parent.addRewrittenQuery(parent.parent.getNodeRewrittenQuery().replace(parent.queryID,parent.getNodeRewrittenQuery()))
						parent = parent.parent