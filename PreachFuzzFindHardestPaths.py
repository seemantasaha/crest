#!/usr/bin/env python3

class Node:
	def __init__(self, id):
		self.id = id
		self.visited = False

	def getID(self):
		return self.id

	def setVisited(self, v):
		self.visited = v

	def isVisited(self):
		return self.visited

class CFG:
	def __init__(self):
		self.rootNode = 0
		self.finalNode = 0
		self.nodeSet = set()
		self.nodeIDDict = {}
		self.nodeWithIncomingEdgeSet = set()
		self.edgeSet = set()
		self.nodeEdgeMappingDict = {}

	def serRootandFinalNode(self):
		tempNodeIDList = []
		for node in self.nodeWithIncomingEdgeSet:
			tempNodeIDList.append(node.getID())
		for node in self.nodeSet:
			if node.getID() not in tempNodeIDList:
				self.rootNode = node
				break

		for node in self.nodeSet:
			if node not in self.nodeEdgeMappingDict:
				self.finalNode = node
				break

	def parseCFG(self, cfgPath):
		cfgFile = open(cfgPath, 'r')
		lines = cfgFile.readlines()
		for line in lines:
			nodeStrList = line.split()
			
			if nodeStrList[0].isdigit():
				nodeID = int(nodeStrList[0])
				startNode = None
				if nodeID in self.nodeIDDict:
					startNode = self.nodeIDDict[nodeID]
				else:
					startNode = Node(nodeID)
					self.nodeIDDict[nodeID] = startNode
				self.nodeSet.add(startNode)

			if len(nodeStrList) > 1 and nodeStrList[1].isdigit():
				nodeID = int(nodeStrList[1])
				trueNode = None
				if nodeID in self.nodeIDDict:
					trueNode = self.nodeIDDict[nodeID]
				else:
					trueNode = Node(nodeID)
					self.nodeIDDict[nodeID] = trueNode
				self.nodeSet.add(trueNode)
				self.edgeSet.add((startNode,trueNode))
				nodeList = []
				nodeList.append(trueNode)
				self.nodeWithIncomingEdgeSet.add(trueNode)
				self.nodeEdgeMappingDict[startNode] = nodeList

			if len(nodeStrList) > 2 and nodeStrList[2].isdigit():
				nodeID = int(nodeStrList[2])
				falseNode = None
				if nodeID in self.nodeIDDict:
					falseNode = self.nodeIDDict[nodeID]
				else:
					falseNode = Node(nodeID)
					self.nodeIDDict[nodeID] = falseNode
				self.nodeSet.add(falseNode)
				self.edgeSet.add((startNode,falseNode))
				self.nodeWithIncomingEdgeSet.add(falseNode)
				self.nodeEdgeMappingDict[startNode].append(falseNode)


	def getRootNode(self):
		return self.rootNode

	def getFinalNode(self):
		return self.finalNode

	def printCFG(self):
		for item in self.nodeEdgeMappingDict:
			if len(self.nodeEdgeMappingDict[item]) == 2:
				#print(self.nodeEdgeMappingDict[item][0])
				#print(self.nodeEdgeMappingDict[item][1])
				print(str(item.getID()) + " -> " 
					+ str(self.nodeEdgeMappingDict[item][0].getID()) + ", " 
					+ str(self.nodeEdgeMappingDict[item][1].getID()))
			else:
				#print(self.nodeEdgeMappingDict[item][0])
				print(str(item.getID()) + " -> " 
					+ str(self.nodeEdgeMappingDict[item][0].getID()))

	def traverseCFG(self):
		self.runDFS(self.rootNode)

	def runDFS(self, node):
		print(node.getID())
		node.setVisited(True)
		if node in self.nodeEdgeMappingDict:
			if len(self.nodeEdgeMappingDict[node]) >= 1:
				if self.nodeEdgeMappingDict[node][0].isVisited() == False: 
					self.runDFS(self.nodeEdgeMappingDict[node][0])
		
			if len(self.nodeEdgeMappingDict[node]) == 2:
				if self.nodeEdgeMappingDict[node][1].isVisited() == False:
					self.runDFS(self.nodeEdgeMappingDict[node][1])

	def printAllPathsUtil(self, u, d, path):
		u.setVisited(True)
		path.append(u.getID())
		if u == d:
			print(path)
		else:
			if len(self.nodeEdgeMappingDict[u]) >= 1:
				if self.nodeEdgeMappingDict[u][0].isVisited() == False: 
					self.printAllPathsUtil(self.nodeEdgeMappingDict[u][0], d, path)
			if len(self.nodeEdgeMappingDict[u]) == 2:
				if self.nodeEdgeMappingDict[u][1].isVisited() == False:
					self.printAllPathsUtil(self.nodeEdgeMappingDict[u][1], d, path)
		path.pop()
		u.setVisited(False)

	def printAllPaths(self, s, d):
		for node in self.nodeSet:
			node.setVisited(False)
		path = []
		self.printAllPathsUtil(s, d, path)


def main(cfgPath,branchConstraintDir):
	cfg = CFG()
	cfg.parseCFG(cfgPath)
	cfg.serRootandFinalNode()
	print("CFG:")
	cfg.printCFG()
	print("Root node: " + str(cfg.getRootNode().getID()))
	print("Final node: " + str(cfg.getFinalNode().getID()))
	cfg.traverseCFG()
	cfg.printAllPaths(cfg.getRootNode(), cfg.getFinalNode())

if __name__ == "__main__":
    
    print("************************************************")
    print("** PReachFuzz: Finding hardest to reach paths **")
    print("************************************************")

    import argparse

    parser = argparse.ArgumentParser(description='Provide the cfg file and directory for branch consraints...')
    parser.add_argument('--cfg_path', metavar='path', required=True,
                        help='the path to cfg file')
    parser.add_argument('--branch_constraints_dir', metavar='dir', required=True,
                        help='path to the directory of all branch constraints')
    args = parser.parse_args()
    main(cfgPath=args.cfg_path, branchConstraintDir=args.branch_constraints_dir)