import os
import sys
import collections

hardestPaths = {}

filename = "logs/combined_paths.txt"
f = open(filename, "r")
paths = f.readlines()

for path in paths:
    key_val = path.strip().split(" : ")
    key = key_val[0]
    val = float(key_val[1])
    hardestPaths[key] = val

f.close()

sp = dict(sorted(hardestPaths.items(), key=lambda item: item[1]))

count = 100
log = ""
for k,v in sp.items():
    log += str(k) + " : " + str(v) + "\n"
    if count == 0:
        break
    count -= 1

filename = "logs/rare_n_paths.txt"
f = open(filename, "w")
f.write(log)
f.close()