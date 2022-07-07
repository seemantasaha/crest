#!/usr/bin/env python3

import os
import sys
import subprocess
import collections

hardestPaths = {}
hardestPathsUsingNodes = {}
hardestPathsUsingLines = {}

pathPrefixDict = {}
pathPrefixPathDict = {}

branchStmtCondMap = {}

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
		self.nodeSet = set()
		self.nodeIDDict = {}
		self.nodeLineDict = {}
		self.nodeProbDict = {}
		self.pathProbDict = {}
		self.nodeWithIncomingEdgeSet = set()
		self.edgeSet = set()
		self.nodeEdgeMappingDict = {}

	def setRootNode(self, rootNode):
		self.rootNode = self.nodeIDDict[int(rootNode)]

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
				if startNode in self.nodeEdgeMappingDict:
					self.nodeEdgeMappingDict[startNode].append(falseNode)
					#branching node, so we need to compute probability from branch constraints
					self.processBranchConstraints(startNode)


	def getRootNode(self):
		return self.rootNode

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
		#print(node.getID())
		node.setVisited(True)
		if node in self.nodeEdgeMappingDict:
			if len(self.nodeEdgeMappingDict[node]) >= 1:
				if self.nodeEdgeMappingDict[node][0].isVisited() == False: 
					self.runDFS(self.nodeEdgeMappingDict[node][0])
		
			if len(self.nodeEdgeMappingDict[node]) == 2:
				if self.nodeEdgeMappingDict[node][1].isVisited() == False:
					self.runDFS(self.nodeEdgeMappingDict[node][1])

	def printAllPathsUtil(self, u, path):
		u.setVisited(True)
		path.append(u.getID())
		if u not in self.nodeEdgeMappingDict:
			#print(path)
			self.computePathProbability(path)
			#self.computePathNodesProbability(path)
			#self.computePathLineNumProbability(path)
		elif u in self.nodeEdgeMappingDict:
			if len(self.nodeEdgeMappingDict[u]) >= 1:
				if self.nodeEdgeMappingDict[u][0].isVisited() == False: 
					self.printAllPathsUtil(self.nodeEdgeMappingDict[u][0], path)
			if len(self.nodeEdgeMappingDict[u]) == 2:
				if self.nodeEdgeMappingDict[u][1].isVisited() == False:
					self.printAllPathsUtil(self.nodeEdgeMappingDict[u][1], path)
		path.pop()
		u.setVisited(False)

	def printAllPaths(self, s):
		for node in self.nodeSet:
			node.setVisited(False)
		path = []
		self.printAllPathsUtil(s, path)

	def computePathProbability(self, path):
		pathNodeStr = ""
		pathLineStr = ""
		pathProb = 1.0
		for nodeID in path:
			if str(nodeID) in self.nodeLineDict and str(self.nodeLineDict[str(nodeID)]) != "-1":
				pathNodeStr += str(nodeID) + "->"
				pathLineStr += str(self.nodeLineDict[str(nodeID)]) + "->"
				if nodeID in self.nodeProbDict:
					pathProb *= self.nodeProbDict[nodeID]
		#print(pathStr + " : " + str(pathProb))
		pathPrefix = pathNodeStr.split("->")[0]
		#print("Path prefix: " + str(pathPrefix))
		if pathPrefix in pathPrefixDict and pathPrefixDict[pathPrefix] > pathProb:
			#print("Path prefix prob: " + str(pathPrefixDict[pathPrefix]))
			#print("Prob: " + str(pathProb))
			if pathPrefixPathDict[pathPrefix] in hardestPaths:
				hardestPaths.pop(pathPrefixPathDict[pathPrefix])
			hardestPaths[(pathNodeStr,pathLineStr)] = pathProb
			pathPrefixDict[pathPrefix] = pathProb
			pathPrefixPathDict[pathPrefix] = (pathNodeStr,pathLineStr)
		elif pathPrefix not in pathPrefixDict:
			hardestPaths[(pathNodeStr,pathLineStr)] = pathProb
			pathPrefixDict[pathPrefix] = pathProb
			pathPrefixPathDict[pathPrefix] = (pathNodeStr,pathLineStr)

	def computePathNodesProbability(self, path):
		pathStr = "Path using nodes: "
		pathProb = 1.0
		for nodeID in path:
			if str(nodeID) in self.nodeLineDict and str(self.nodeLineDict[str(nodeID)]) != "-1":
				pathNodeStr += str(nodeID) + "->"
				if nodeID in self.nodeProbDict:
					pathProb *= self.nodeProbDict[nodeID]
		#print(pathStr + " : " + str(pathProb))
		hardestPathsUsingNodes[pathStr] = pathProb

	def computePathLineNumProbability(self, path):
		pathStr = "Path using lines: "
		pathProb = 1.0
		for nodeID in path:
			if str(nodeID) in self.nodeLineDict and str(self.nodeLineDict[str(nodeID)]) != "-1":
				pathStr += str(self.nodeLineDict[str(nodeID)]) + "->"
				if nodeID in self.nodeProbDict:
					pathProb *= self.nodeProbDict[nodeID]
		#print(pathStr + " : " + str(pathProb))
		hardestPathsUsingLines[pathStr] = pathProb 

	def modelCount(self, consPath):
		print(consPath)
		process = subprocess.Popen(["abc", "-i", consPath, "-bi", "15", "-v", "0"], stdout = subprocess.PIPE)
		result = process.communicate()[0].decode('utf-8')
		#process.terminate()
		print(result)
		lines = result.split('\n');
		print(lines)
		count = 0
		flag = False
		if lines[0] == "sat":
			count = int(lines[1])
		else:
			flag = True
		return (count, flag)

	def computeBranchProbability(self, nodeID, consPath):
		if not os.path.exists(consPath):
			print("No constraint for this branch!!! : " + consPath)
			nodeList = self.nodeEdgeMappingDict[self.nodeIDDict[nodeID]]
			self.nodeProbDict[nodeList[0].getID()] = 0.5
			self.nodeProbDict[nodeList[1].getID()] = 0.5
			return
		trueCount, flag = self.modelCount(consPath)
		print("True branch model count: " + str(trueCount))

		if flag:
			trueProb, falseProb = 0.5, 0.5
		else:
			intDomainSize = self.computeDomain(consPath)
			if intDomainSize == 1: #special case that needs to be fixed
				trueProb = 0.5
			else:
				trueProb = trueCount / intDomainSize
			falseProb = 1.0 - trueProb

		nodeList = self.nodeEdgeMappingDict[self.nodeIDDict[nodeID]]
		self.nodeProbDict[nodeList[0].getID()] = trueProb
		self.nodeProbDict[nodeList[1].getID()] = falseProb

	def computeDomain(self, consPath):
		intDomainSize = 1
		consFile = open(consPath, 'r')
		lines = consFile.readlines()
		for line in lines:
			if "(assert (and (>= " in line and " 0) (<= " in line and " 255)))" in line:
				intDomainSize *= 256
			elif "(assert (and (>= " in line and " (- 128))) (<= " in line and " 127)))" in line:
				intDomainSize *= 256
			elif "(assert (and (>= " in line and " 0)) (<= " in line and " 1)))" in line:
				intDomainSize *= 2
			elif "(assert (and (>= " in line and " 0)) (<= " in line and " 32767)))" in line:
				intDomainSize *= 2**15
			elif "(assert (and (>= " in line and " (- 32768)) (<= " in line and " 32767)))" in line:
				intDomainSize *= 2*(2**15)
		print("Domain size for this constraint is: " + str(intDomainSize))
		return intDomainSize


	def processBranchConstraints(self, branchNode):
		nodeID = branchNode.getID()
		if nodeID >= 671635 and nodeID <= 677065:
			consPath = self.branchConstraintsDir + "/" + "branch_" + str(nodeID) + ".smt2"
			self.computeBranchProbability(nodeID, consPath)

	def setLineNumbers(self):
		branchesPath = self.branchConstraintsDir + "/" + "branch_statements"
		branchesFile = open(branchesPath, 'r')
		lines = branchesFile.readlines()
		for line in lines[1:]:
			if not line.startswith("Expression"):
				lineInfo = line.split(", ")
				trueNodeID = lineInfo[2]
				falseNodeID = lineInfo[3]
				self.nodeLineDict[trueNodeID] = lineInfo[6].split(":")[1]
				self.nodeLineDict[falseNodeID] = lineInfo[7].split(":")[1].split("\n")[0]


def main(cfgPath,branchConstraintDir):
	cfg = CFG(cfgPath,branchConstraintDir)
	cfg.parseCFG()
	cfg.setLineNumbers()
	print("CFG:")
	cfg.printCFG()

	branchStmtsPath = branchConstraintDir + "/branch_statements"
	stmtFile = open(branchStmtsPath, 'r')
	lines = stmtFile.readlines()
	for line in lines:
		if not line.startswith("Expression"):
			lineInfo = line.split("\n")[0].split(", ")
			cond = lineInfo[0]
			b1 = lineInfo[2]
			b2 = lineInfo[3]
			#print((cond,b1,b2))
			branchStmtCondMap[b1] = "(" + cond + ")"
			branchStmtCondMap[b2] = "(not (" + cond + ")"

	cfgFunMapPath = cfgPath + "_func_map"
	funcFile = open(cfgFunMapPath, 'r')
	lines = funcFile.readlines()
	for line in lines:
		lineInfo = line.split("\n")[0].split(" ")
		funcName = lineInfo[0]
		funcRootNode = lineInfo[1]
		if funcName == "main" and funcRootNode == "671635": #strings.c
			#print("Root node: " + funcRootNode)
			cfg.setRootNode(funcRootNode)
			cfg.traverseCFG()
			cfg.printAllPaths(cfg.getRootNode())

	#sp = collections.OrderedDict(sorted(hardestPaths.items()))
	sp = dict(sorted(hardestPaths.items(), key=lambda item: item[1]))
	print("\n\n\n----------------------------------------------------------------------------------------------------------")
	print("Hardest paths for fuzzer [Format: Sequence of nodes (Sequence of line numbers)\nConditions along the path]")
	print("----------------------------------------------------------------------------------------------------------\n\n\n")
	count = 20
	for k,v in sp.items():
		print(str(k[0])+"("+str(k[1])+")"+ ": " + str(v))
		pathCond = ""
		path = k[0].split("->")
		for br in path:
			if br != "":
				pathCond += branchStmtCondMap[str(br)] + " and "
		print(pathCond[:-5])
		print("\n\n")
		if count == 0:
			break
		count -= 1

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