import os
import sys

log = ""
log_set = set()

logDir = "/home/seem/Research/libxml2/ex_log"
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
    if asc.isdigit():   
        logString += chr(int(asc)) 

filename = "rare_seeds.txt"
f = open(filename, "w")
f.write(logString)
f.close()