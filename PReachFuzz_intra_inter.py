#!/usr/bin/env python3

import os
import sys
import subprocess
import collections
from datetime import datetime
from difflib import SequenceMatcher
from fuzzywuzzy import fuzz

hardestPaths = {}
hardestPathsUsingNodes = {}
hardestPathsUsingLines = {}
lastPathNodeStr = ""
lastPathLineStr = ""

branchStmtCondMap = {}

loop_bound = 1

numPath = 0
log = ""
count = 1

def printString(string):
	global numPath
	global log
	global count
	numPath += 1
	if numPath >= 5000:
		filename = "logs/paths_upto_" + str(count) + ".txt"
		f = open(filename, "w")
		f.write(log)
		f.close()
		print("File written up to line: " + str(count))
		log = ""
		numPath = 0
	log += str(string) + "\n"
	count += 1

def writeRemainingLogs():
	global numPath
	global count
	if log != "":
		filename = "logs/paths_upto_" + str(count) + ".txt"
		f = open(filename, "w")
		f.write(log)
		f.close()
		print("File written up to line: " + str(count))

def similar(a, b):
    #return SequenceMatcher(None, a, b).ratio()
    return fuzz.ratio(a, b)

def printHardestPaths():
	print(len(hardestPaths))
	sp = dict(sorted(hardestPaths.items(), key=lambda item: item[1]))
	print("\n\n\n----------------------------------------------------------------------------------------------------------")
	print("Hardest paths for fuzzer [Format: Sequence of nodes (Sequence of line numbers)\nConditions along the path]")
	print("----------------------------------------------------------------------------------------------------------\n\n\n")
	count = 1000
	#print(len(sp))
	for k,v in sp.items():
		print(str(k[0])+"("+str(k[1])+")"+ ": " + str(v))
		#pathCond = ""
		#path = k[0].split("->")
		#for br in path:
		#	if br != "":
		#		pathCond += branchStmtCondMap[str(br)] + " and "
		#print(pathCond[:-5])
		#print("\n\n")
		if count == 0:
			break
		count -= 1

class Node:
	def __init__(self, id):
		self.id = id
		self.visited = 0

	def getID(self):
		return self.id

	def setVisited(self, v):
		if v == True:
			self.visited += 1
		else:
			self.visited = 0

	def isVisited(self):
		return self.visited >= loop_bound

class CFG:
	def __init__(self, cfgPath, branchConstraintsDir, depFile):
		self.cfgPath = cfgPath
		self.branchConstraintsDir = branchConstraintsDir
		self.depFile = depFile
		self.rootNode = 0
		self.nodeSet = set()
		self.depLineSet = set()
		self.nodeIDDict = {}
		self.nodeLineDict = {}
		self.nodeProbDict = {}
		self.pathProbDict = {}
		self.nodeWithIncomingEdgeSet = set()
		self.edgeSet = set()
		self.nodeEdgeMappingDict = {}
		self.pathPrefixProbDict = {}
		self.pathPrefixLineDict = {}
		self.memoized = 0

	def setRootNode(self, rootNode):
		self.rootNode = self.nodeIDDict[int(rootNode)]

	def parseCFG(self):

		cfgFile = open(self.cfgPath, 'r')
		lines = cfgFile.readlines()
		for line in lines:
			#print(line)
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
				#print(startNode.getID())
				if startNode in self.nodeEdgeMappingDict:
					self.nodeEdgeMappingDict[startNode].append(falseNode)
					#branching node, so we need to compute probability from branch constraints
					#if not startNode.getID() in self.nodeProbDict:
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

	def printAllPathsUtil(self, u, pathNodeStr, startTime):
		now = datetime.now()
		delta = now - startTime
		if delta.total_seconds() >= 8640:
			#printHardestPaths()
			writeRemainingLogs()
			print("Number of times memoized: " + str(self.memoized))
			exit()
			#os.system('reboot now')
		if pathNodeStr.count("->") >= 60:
			self.computePathProbability(pathNodeStr)
			return
		u.setVisited(True)
		uID = u.getID()

		if str(uID) in self.nodeLineDict:
			pathNodeStr += str(uID) + "->"
		if u not in self.nodeEdgeMappingDict:
			self.computePathProbability(pathNodeStr)
			#self.computePathNodesProbability(path)
			#self.computePathLineNumProbability(path)
		elif u in self.nodeEdgeMappingDict:
			probPriorityFlag = False
			if len(self.nodeEdgeMappingDict[u]) >= 2:
				leftNodeIDProb = self.nodeProbDict[self.nodeEdgeMappingDict[u][0].getID()]
				rightNodeIDProb = self.nodeProbDict[self.nodeEdgeMappingDict[u][1].getID()]
				#print("Left node: " + str(self.nodeEdgeMappingDict[u][0].getID()))
				#print("Right node: " + str(self.nodeEdgeMappingDict[u][1].getID()))
				#print("Left node probability: " + str(leftNodeIDProb))
				#print("Right node probability: " + str(rightNodeIDProb))
				if leftNodeIDProb > rightNodeIDProb:
					#print("probPriorityFlag")
					probPriorityFlag = True
				#if str(uID) == "131529":
				#	probPriorityFlag = True
			
			if probPriorityFlag == False:				
				if len(self.nodeEdgeMappingDict[u]) >= 2:
					if self.nodeEdgeMappingDict[u][0].isVisited() == False:
						#print("Going to " + str(self.nodeEdgeMappingDict[u][0].getID()))
						self.printAllPathsUtil(self.nodeEdgeMappingDict[u][0], pathNodeStr, startTime)
					if self.nodeEdgeMappingDict[u][1].isVisited() == False:
						#print("Going to " + str(self.nodeEdgeMappingDict[u][1].getID()))
						self.printAllPathsUtil(self.nodeEdgeMappingDict[u][1], pathNodeStr, startTime)
				else:
					if self.nodeEdgeMappingDict[u][0].isVisited() == False:
						#print("Going to " + str(self.nodeEdgeMappingDict[u][0].getID())) 
						self.printAllPathsUtil(self.nodeEdgeMappingDict[u][0], pathNodeStr, startTime)
			else:
				if len(self.nodeEdgeMappingDict[u]) >= 2:
					if self.nodeEdgeMappingDict[u][1].isVisited() == False:
						#print("Going to " + str(self.nodeEdgeMappingDict[u][1].getID())) 
						self.printAllPathsUtil(self.nodeEdgeMappingDict[u][1], pathNodeStr, startTime)
					if self.nodeEdgeMappingDict[u][0].isVisited() == False: 
						#print("Going to " + str(self.nodeEdgeMappingDict[u][0].getID())) 
						self.printAllPathsUtil(self.nodeEdgeMappingDict[u][0], pathNodeStr, startTime)
				else:
					if self.nodeEdgeMappingDict[u][0].isVisited() == False: 
						#print("Going to " + str(self.nodeEdgeMappingDict[u][0].getID())) 
						self.printAllPathsUtil(self.nodeEdgeMappingDict[u][0], pathNodeStr, startTime)

		if str(uID) in self.nodeLineDict:
			lastPos = pathNodeStr.rfind("-")
			pathNodeStr = pathNodeStr[:lastPos]
			lastPos = pathNodeStr.rfind("-")
			pathNodeStr = pathNodeStr[:lastPos] + "->"
			
		u.setVisited(False)

	def printAllPaths(self, s, startTime):
		for node in self.nodeSet:
			node.setVisited(False)
		pathNodeStr = ""
		self.printAllPathsUtil(s, pathNodeStr, startTime)

	def computePathProbability(self, pathNodeStr):
		
		pathLineStr = ""
		pathProb = 1.0
		lastPathNodeStr = pathNodeStr

		lastPos = lastPathNodeStr.rfind("-")
		lastPathNodeStr = lastPathNodeStr[:lastPos]
		lastPos = lastPathNodeStr.rfind("-")
		nodeID = int(lastPathNodeStr[lastPos+2:])
		lastPathNodeStr = lastPathNodeStr[:lastPos] + "->"

		flagToNotRunForwardMemoization = False

		while True:
			if str(nodeID) in self.nodeLineDict:
				pathLineStr = str(self.nodeLineDict[str(nodeID)]) + "->" + pathLineStr
			else:
				pathLineStr = "-1" + "->" + pathLineStr

			if nodeID in self.nodeProbDict: 
				if len(self.depLineSet) == 0:
					pathProb *= self.nodeProbDict[nodeID]
				elif str(self.nodeLineDict[str(nodeID)]) in self.depLineSet:
					pathProb *= self.nodeProbDict[nodeID]
				else:
					pass


			if lastPathNodeStr == "":
				self.pathPrefixLineDict[pathNodeStr] = pathLineStr
				self.pathPrefixProbDict[pathNodeStr] = pathProb
				break

			elif lastPathNodeStr in self.pathPrefixProbDict:
				pathProb = self.pathPrefixProbDict[lastPathNodeStr] * pathProb
				pathLineStr = str(self.pathPrefixLineDict[lastPathNodeStr]) + pathLineStr
				self.pathPrefixLineDict[pathNodeStr] = pathLineStr
				self.pathPrefixProbDict[pathNodeStr] = pathProb
				flagToNotRunForwardMemoization = True
				self.memoized +=1
				break

			else:
				#probComputedPathNodeStr = pathNodeStr[len(lastPathNodeStr):]
				#self.pathPrefixLineDict[probComputedPathNodeStr] = pathLineStr
				#self.pathPrefixProbDict[probComputedPathNodeStr] = pathProb
				lastPos = lastPathNodeStr.rfind("-")
				lastPathNodeStr = lastPathNodeStr[:lastPos]
				lastPos = lastPathNodeStr.rfind("-")
				if lastPos != -1:
					nodeID = int(lastPathNodeStr[lastPos+2:])
					lastPathNodeStr = lastPathNodeStr[:lastPos] + "->"
				else:
					nodeID = int(lastPathNodeStr)
					lastPathNodeStr = ""


		if not flagToNotRunForwardMemoization:

			pathLineStr = ""
			pathProb = 1.0

			nodes = pathNodeStr.split("->")
			partialPathNodeStr = ""
			partialPathLineStr = ""
			for nodeID in nodes:
				
				partialPathNodeStr += str(nodeID) + "->"
				if str(nodeID) in self.nodeLineDict:
					partialPathLineStr += str(self.nodeLineDict[str(nodeID)]) + "->"
				else:
					partialPathLineStr += "-1" + "->"
				
				if nodeID != "":
					nodeID = int(nodeID)
					if nodeID in self.nodeProbDict: 
						if len(self.depLineSet) == 0:
							pathProb *= self.nodeProbDict[nodeID]
						elif str(self.nodeLineDict[str(nodeID)]) in self.depLineSet:
							pathProb *= self.nodeProbDict[nodeID]
						else:
							pass
					self.pathPrefixProbDict[partialPathNodeStr] = pathProb
					self.pathPrefixLineDict[partialPathNodeStr] = partialPathLineStr
		
		if pathProb > 1.0e-50:
			return

		printString(pathNodeStr + "(" + pathLineStr + ") : " + str(pathProb))
		
		if "->6607" in pathLineStr or "->5421" in pathLineStr or "->5984" in pathLineStr or "->5339" in pathLineStr:
			#printString(pathNodeStr + "(" + pathLineStr + ") : " + str(pathProb))
			now = datetime.now()
			current_time = now.strftime("%H:%M:%S")
			print("Current Time =", current_time)

	


	def modelCount(self, consPath):
		#print(consPath)
		process = subprocess.Popen(["abc", "-i", consPath, "-bi", "15", "-v", "0"], stdout = subprocess.PIPE)
		result = process.communicate()[0].decode('utf-8')
		#process.terminate()
		#print(result)
		lines = result.split('\n')
		#print(lines)
		count = 0
		flag = False
		if lines[0] == "sat":
			count = int(lines[1])
		else:
			flag = True
		return (count, flag)

	def computeBranchProbability(self, nodeID, consPath):
		if not os.path.exists(consPath):
			#print("No constraint for this branch!!! : " + consPath)
			nodeList = self.nodeEdgeMappingDict[self.nodeIDDict[nodeID]]
			self.nodeProbDict[nodeList[0].getID()] = 1.0
			self.nodeProbDict[nodeList[1].getID()] = 1.0
			return
		with open(consPath) as f:
			lines = f.readlines()
			for line in lines:
				if "declare-fun" in line and "xml" in line:
					nodeList = self.nodeEdgeMappingDict[self.nodeIDDict[nodeID]]
					self.nodeProbDict[nodeList[0].getID()] = 1.0
					self.nodeProbDict[nodeList[1].getID()] = 1.0
					return
		#trueCount, flag = self.modelCount(consPath)
		countPath = consPath.replace("smt2","count")
		if os.path.exists(countPath):
			#print("Count file for " + str(countPath))
			f = open(countPath,'r')
			line = f.readline()
			part = line.split(",")
		else:
			#print("No count file for " + str(countPath))
			part = [1,2,True]
		trueCount, flag = int(part[0]), part[2]
		#print("True branch model count: " + str(trueCount))

		trueProb, falseProb = 0.0, 0.0
		if flag == "True":
			trueProb, falseProb = 1.0, 1.0
		else:
			#intDomainSize = self.computeDomain(consPath)
			intDomainSize = int(part[1])
			#print("Domain: " + str(intDomainSize))
			if intDomainSize == 1: #special case that needs to be fixed
				trueProb = 1.0
				falseProb = 1.0
			else:
				trueProb = trueCount / intDomainSize
				falseProb = 1.0 - trueProb
			if trueProb >= 1.0: #temp fix
				trueProb = 1.0
				falseProb = 1.0
		#print(trueProb, falseProb)
		nodeList = self.nodeEdgeMappingDict[self.nodeIDDict[nodeID]]
		self.nodeProbDict[nodeList[0].getID()] = trueProb
		self.nodeProbDict[nodeList[1].getID()] = falseProb
		
		#line_st = str(nodeList[0].getID()) + ": " + str(trueProb) + "\n" + str(nodeList[1].getID()) + ": " + str(falseProb) + "\n"
		#with open('strings_probability.txt', 'a') as f:
		#	f.write(line_st)

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
		#print("Domain size for this constraint is: " + str(intDomainSize))
		return intDomainSize


	def processBranchConstraints(self, branchNode):
		nodeID = branchNode.getID()
		#print("processing constraint for branch: " + str(nodeID))
		#if nodeID >= 4635458 and nodeID <= 4652062:
		consPath = self.branchConstraintsDir + "/" + "branch_" + str(nodeID) + ".smt2"
		self.computeBranchProbability(nodeID, consPath)

	def setLineNumbers(self):
		branchesPath = self.branchConstraintsDir + "/" + "branch_statements"
		branchesFile = open(branchesPath, 'r')
		lines = branchesFile.readlines()
		#print("Number of lines: ", len(lines))
		for line in lines: 
			if not line.startswith("Expression"):
				lineInfo = line.split(", ")
				trueNodeID = lineInfo[2]
				falseNodeID = lineInfo[3]
				#print(trueNodeID)
				#print(falseNodeID)
				
				self.nodeLineDict[trueNodeID] = lineInfo[6].split(":")[1]
				self.nodeLineDict[falseNodeID] = lineInfo[7].split(":")[1].split("\n")[0]
				
				#self.nodeLineDict[trueNodeID] = lineInfo[6]
				#self.nodeLineDict[falseNodeID] = lineInfo[7].split("\n")[0]

	def setDependentLineNumbers(self):
		f = open(self.depFile, "r")
		content = f.read()
		lineNumbers = content.split(" ")
		for line in lineNumbers:
			self.depLineSet.add(line)


def main(cfgPath,branchConstraintDir, depFile):

	startTime = datetime.now()
	current_time = startTime.strftime("%H:%M:%S")
	print("Current Time =", current_time)

	cfg = CFG(cfgPath,branchConstraintDir, depFile)

	cfg.parseCFG()
	#print("[Done] parsing CFG.")

	cfg.setLineNumbers()
	if depFile != None:
		cfg.setDependentLineNumbers()
	#print("[Done] setting line numbers.")
	#print("CFG:")
	#cfg.printCFG()

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

	'''
	cfgFunMapPath = cfgPath + "_func_map"
	funcFile = open(cfgFunMapPath, 'r')
	lines = funcFile.readlines()
	for line in lines:
		lineInfo = line.split("\n")[0].split(" ")
		funcName = lineInfo[0]
		funcRootNode = lineInfo[1]
		if funcName == "xmlParseDocument" and funcRootNode == "3149369":
		#print("Root node: " + funcRootNode)
			cfg.setRootNode(funcRootNode)
			cfg.traverseCFG()
			cfg.printAllPaths(cfg.getRootNode())
	'''
	funcRootNode = 4648324
	#funcRootNode = 2331618
	#funcRootNode = 270342
	
	cfg.setRootNode(funcRootNode)

	cfg.printAllPaths(cfg.getRootNode(), startTime)

	writeRemainingLogs()

	#printHardestPaths()

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
    parser.add_argument('--dependent_node_file', metavar='path', required=False,
                        help='path to the file of taint analysis result')
    args = parser.parse_args()
    main(cfgPath=args.cfg_path, branchConstraintDir=args.branch_constraints_dir, depFile=args.dependent_node_file)