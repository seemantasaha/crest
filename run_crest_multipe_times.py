import os
import sys
import collections

filename = "/home/seem/Research/crest/libxml2-intra-2.4hrs-logs/clear_rare_n_paths.txt"
f = open(filename, "r")
paths = f.readlines()

count = 1
for path in paths:
    command = "time ../crest/bin/run_crest './xmllint test.xml' 10 -pge \"" + path + "\" > ex_log/log_" + str(count) + ".txt"
    print(command)
    os.system(command)
    count += 1