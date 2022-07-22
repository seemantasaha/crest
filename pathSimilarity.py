import sys
import os

from fuzzywuzzy import fuzz

desired_paths = []

def similar(a, b):
    return fuzz.ratio(a, b)

num_files = 0
total_desired_paths = []
for filename in os.listdir("logs"):
    with open(os.path.join("logs", filename), 'r') as f:
        paths = f.readlines()
        desired_paths = []
        desired_paths.append(paths[0])
        count = 0
        for path1 in paths[1:]:
            addFlag = True
            removeAddFlag = False
            path1NodeStr = path1.split("(")[0]
            for path2 in desired_paths:
                path2NodeStr = path2.split("(")[0]
                sim = similar(path1NodeStr, path2NodeStr)
                if sim >= 95:
                    addFlag  = False
                    if len(path1NodeStr) > len(path2NodeStr):
                        removeAddFlag = True
                    break
            if removeAddFlag == True:
                desired_paths.remove(path2)
                desired_paths.append(path1)
            elif addFlag == True:
                desired_paths.append(path1)
                count += 1
        #print("Number of paths to consider: " + str(count))
        num_files += 1
        total_desired_paths.extend(desired_paths)

print("Number of files: " + str(num_files))

print("Number of desired paths: " + str(len(total_desired_paths)))
log = ""
for path in total_desired_paths:
    log += path

filename = "logs/combined_paths.txt"
f = open(filename, "w")
f.write(log)
f.close()
    

