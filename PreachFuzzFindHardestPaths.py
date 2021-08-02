#!/usr/bin/env python3

import os
import sys
import subprocess

intDomainSize = 2**32

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
	def __init__(self, cfgPath, branchConstraintsDir):
		self.cfgPath = cfgPath
		self.branchConstraintsDir = branchConstraintsDir
		self.rootNode = 0
		self.finalNode = 0
		self.nodeSet = set()
		self.nodeIDDict = {}
		self.nodeLineDict = {}
		self.nodeProbDict = {}
		self.pathProbDict = {}
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

	def parseCFG(self):
		cfgFile = open(self.cfgPath, 'r')
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
				#branching node, so we need to compute probability from branch constraints
				self.processBranchConstraints(startNode)


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
			self.computePathProbability(path)
			self.computePathLineNumProbability(path)
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

	def computePathProbability(self, path):
		pathStr = ""
		pathProb = 1.0
		for nodeID in path:
			pathStr += str(nodeID) + "->"
			if nodeID in self.nodeProbDict:
				pathProb *= self.nodeProbDict[nodeID]
		print(pathStr + " : " + str(pathProb))

	def computePathLineNumProbability(self, path):
		pathStr = ""
		pathProb = 1.0
		for nodeID in path:
			if str(nodeID) in self.nodeLineDict:
				pathStr += str(self.nodeLineDict[str(nodeID)]) + "->"
				if nodeID in self.nodeProbDict:
					pathProb *= self.nodeProbDict[nodeID]
		print(pathStr + " : " + str(pathProb))   

	def modelCount(self, consPath):
		print(consPath)
		process = subprocess.Popen(["abc", "-i", consPath, "-bi", "31", "-v", "0"], stdout = subprocess.PIPE)
		result = process.communicate()[0].decode('utf-8')
		process.terminate()
		print(result)
		lines = result.split('\n');
		print(lines)
		count = 0
		if lines[0] == "sat":
			count = int(lines[1])
		return count

	def computeBranchProbability(self, nodeID, constraint):
		trueCount = self.modelCount(constraint)
		print("True branch mode count: " + str(trueCount))
		trueProb = trueCount / intDomainSize
		falseProb = 1.0 - trueProb

		nodeList = self.nodeEdgeMappingDict[self.nodeIDDict[nodeID]]
		self.nodeProbDict[nodeList[0].getID()] = trueProb
		self.nodeProbDict[nodeList[1].getID()] = falseProb

	def processBranchConstraints(self, branchNode):
		nodeID = branchNode.getID()
		consPath = self.branchConstraintsDir + "/" + "branch_" + str(nodeID) + ".smt2"
		self.computeBranchProbability(nodeID, consPath)

	def setLineNumbers(self):
		branchesPath = self.branchConstraintsDir + "/" + "branch_statements"
		branchesFile = open(branchesPath, 'r')
		lines = branchesFile.readlines()
		for line in lines[1:]:
			lineInfo = line.split(", ")
			trueNodeID = lineInfo[2]
			falseNodeID = lineInfo[3]
			self.nodeLineDict[trueNodeID] = lineInfo[6].split(":")[1]
			self.nodeLineDict[falseNodeID] = lineInfo[7].split(":")[1].split("\n")[0]


def main(cfgPath,branchConstraintDir):
	cfg = CFG(cfgPath,branchConstraintDir)
	cfg.parseCFG()
	cfg.serRootandFinalNode()
	cfg.setLineNumbers()

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