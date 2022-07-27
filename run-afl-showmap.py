import os
import sys
import subprocess
import time

def check_output(command, console):
    if console == True:
        process = subprocess.Popen(command)
    else:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    output, error = process.communicate()
    returncode = process.poll()
    return returncode, output, error

for filename in os.listdir("queue_backup"):
    if not "id" in filename:
        continue
    with open(os.path.join("queue_backup", filename), 'r') as f:
        in_filename = "queue_backup/" + filename
        out_filename = in_filename + ".out"
        command = "afl-showmap -o " + out_filename + " ../xmllint " + in_filename
        print(command)
        #returncode, output, error = check_output(command, False)
        #if returncode != 0:
        #    print("Process failed")
        #    sys.exit()
        os.system(command)
        time.sleep(0.25)