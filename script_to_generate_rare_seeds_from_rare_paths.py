from curses.ascii import isdigit
import sys
import os

def main(path, projectDir, binaryArg):

    logDir = projectDir + "/ex_log"
    num = 1
    count = 50
    
    with open(path, 'r') as f:

        lines = f.readlines()

        for line in lines:

            path_node = line.split("(")[0]
            path_node = path_node.strip()
            path_node = path_node.replace("->"," ")
            
            command = "cd " + projectDir + " && time ../crest/bin/run_crest '" + binaryArg + "' 10 -pge \"" + path_node[:-1] + "\" > " + logDir + "/log_" + str(num) + ".txt"
            print(command)

            os.system(command)

            num += 1

            if count == 0:
                break
            count -= 1


    log = ""
    log_set = set()

    for filename in os.listdir(logDir):
        with open(os.path.join(logDir, filename), 'r', errors='replace') as f:
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
        if asc.isdigit():   
            logString += chr(int(asc)) 

    filename = "rare_seeds.txt"
    f = open(filename, "w")
    f.write(logString)
    f.close()



if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description='Provide the path directory, project directory and binary with arguments...')
    parser.add_argument('--path', metavar='path', required=True, help='the path')
    parser.add_argument('--project', metavar='dir', required=True, help='the project directory')
    parser.add_argument('--bin_args', metavar='path', required=True, help='the binary and arguments if any')
    args = parser.parse_args()
    main(path=args.path, projectDir=args.project, binaryArg=args.bin_args)