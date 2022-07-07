import sys
import os
import subprocess

nodeLineDict = {}
branchesPath = "/home/seem/Research/libxml2/translation/branch_statements"
branchesFile = open(branchesPath, 'r')
lines = branchesFile.readlines()
for line in lines: 
  if not line.startswith("Expression"):
    lineInfo = line.split(", ")
    trueNodeID = lineInfo[2]
    falseNodeID = lineInfo[3]
    nodeLineDict[trueNodeID] = lineInfo[6].split(":")[1]
    nodeLineDict[falseNodeID] = lineInfo[7].split(":")[1].split("\n")[0]

symPathFile = open("/home/seem/Research/crest/nodes.txt", 'r')
lines = symPathFile.readlines()
st = ""
for line in lines: 
  node = line.strip()
  st += node + " -> " + str(nodeLineDict[node]) + "\n"
symPathFile = open("/home/seem/Research/crest/nodeWithLines.txt", 'w')
symPathFile.write(st)

