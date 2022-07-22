import sys
import os

log = ""
log_set = set()
for filename in os.listdir("ex_log"):
    with open(os.path.join("ex_log", filename), 'r') as f:
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

filename = "combined_inputs.txt"
f = open(filename, "w")
f.write(log)
f.close()
