import os
import sys


tuple_dict = {}
total_count = 0
for filename in os.listdir("queue_backup"):
    if not "out" in filename:
        continue
    with open(os.path.join("queue_backup", filename), 'r') as f:
        lines = f.readlines()
        count = 0
        unique_count = 0

        for line in lines:
            key_val = line.strip().split(":")
            key = key_val[0]
            val = int(key_val[1])
            if key in tuple_dict:
                tuple_dict[key] += val
            else:
                tuple_dict[key] = val
                unique_count += 1
                total_count += 1
            count +=1
            
        print("Number of tuples for input file " + filename + " : " + str(count))
        print("Unique number of tuples for input file " + filename + " : " + str(unique_count))
        print("Total number of tuples : " + str(total_count))
