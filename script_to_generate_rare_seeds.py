import sys
import os

from fuzzywuzzy import fuzz

desired_paths = []

def similar(a, b):
    return fuzz.ratio(a, b)

def main(pathDir, projectDir, binaryWithArg):
    num_files = 0
    total_desired_paths = []
    logDir = projectDir + "/ex_log"

    print("Path directory: "+ pathDir)
    print("Project directory: "+ projectDir)
    print("Log directory: "+ logDir)

    for filename in os.listdir(pathDir):
        print("Processing ... " + filename)
        with open(os.path.join(pathDir, filename), 'r') as f:
            paths = f.readlines()
            desired_paths = []
            desired_paths.append(paths[0])
            count = 1
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
            print("Number of paths to consider: " + str(count))
            num_files += 1
            total_desired_paths.extend(desired_paths)

    print("Number of files: " + str(num_files))

    print("Number of desired paths: " + str(len(total_desired_paths)))


    hardestPaths = {}

    for path in total_desired_paths:
        key_val = path.strip().split(" : ")
        key = key_val[0]
        val = float(key_val[1])
        hardestPaths[key] = val

    sp = dict(sorted(hardestPaths.items(), key=lambda item: item[1]))

    count = 100

    if not os.path.exists(logDir):
        os.makedirs(logDir)
    else:
        rmCommand = "rm " + logDir + "/*"
        os.system(rmCommand)

    num = 1
    for k,v in sp.items():
        path_node = str(k).strip().split("(")[0]
        path_node = path_node.strip()
        path_node = path_node.replace("->"," ")
        
        command = "cd " + projectDir + " && time ../crest/bin/run_crest '" + binaryWithArg + "' 10 -pge \"" + path_node[:-1] + "\" > " + logDir + "/log_" + str(num) + ".txt"
        print(command)

        os.system(command)

        num += 1

        if count == 0:
            break
        count -= 1


    log = ""
    log_set = set()

    for filename in os.listdir(logDir):
        with open(os.path.join(logDir, filename), 'r') as f:
            print("File: " + str(filename))
            lines = f.readlines()
        
            lines_reverse = lines[::-1]
            following_line = ""
            for line in lines_reverse:
                if line.startswith("inputs"):
                    print("Found input")
                    if following_line not in log_set:
                        log_set.add(following_line)
                        log += following_line.strip() + "\n 10 10 \n" # ascii 10 is a newlinr
                    else:
                        print("but not a new input")
                    break
                following_line = line

    #convert rare seeds from ascii to string
    ascii_vals = log.split()
    logString = ""
    for asc in ascii_vals:
        logString += chr(int(asc)) 

    filename = "rare_seeds.txt"
    f = open(filename, "w")
    f.write(logString)
    f.close()



if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description='Provide the path directory, project directory and binary with arguments...')
    parser.add_argument('--path_dir', metavar='dir', required=True, help='the path directory')
    parser.add_argument('--project_dir', metavar='dir', required=True, help='the project directory')
    parser.add_argument('--bin_args', metavar='path', required=True, help='the binary and arguments if any')
    args = parser.parse_args()
    main(pathDir=args.path_dir,projectDir=args.project_dir,binaryWithArg=args.bin_args)