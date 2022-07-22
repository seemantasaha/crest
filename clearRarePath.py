import os
import sys
import collections

hardestPaths = {}

filename = "rare_n_paths.txt"
f = open(filename, "r")
paths = f.readlines()

log = ""
for path in paths:
    path_node = path.strip().split("(")[0]
    log += path_node + "\n"

f.close()

filename = "clear_rare_n_paths.txt"
f = open(filename, "w")
f.write(log)
f.close()