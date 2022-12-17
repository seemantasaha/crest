from curses.ascii import isdigit
import sys
import os

from fuzzywuzzy import fuzz

desired_paths = []

def similar(a, b):
    return fuzz.ratio(a, b)

def main(pathDir):
    num_files = 0
    total_desired_paths = []

    print("Path directory: "+ pathDir)

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
        if " : " not in path:
            continue
        key_val = path.strip().split(" : ")
        key = key_val[0]
        val = float(key_val[1])
        hardestPaths[key] = val

    sp = dict(sorted(hardestPaths.items(), key=lambda item: item[1]))

    count = 100

    num = 1
    rare_paths = ""
    for k,v in sp.items():
        rare_paths += str(k) + " : " + str(v) + "\n"
        #print(str(k) + " : " + str(v) + "\n")
        if count <= 0:
            break
        count -= 1

    os.system("echo \"" + rare_paths + "\" > rare_paths.txt")



if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description='Provide the path directory, project directory and binary with arguments...')
    parser.add_argument('--path_dir', metavar='dir', required=True, help='the path directory')
    args = parser.parse_args()
    main(pathDir=args.path_dir)