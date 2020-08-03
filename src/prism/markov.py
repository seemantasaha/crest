import argparse as ap
import re
import json
import os.path
from os import path
from utils.Shell import Shell
#Markov Chain
markov = {}
last_state = 0

def parse(cfg, branches, translation):
    global markov
    global last_state
    shell = Shell()
    cfg_f = open(cfg)
    branches_f = open(branches)
    for line in cfg_f:
        edges = line.split()
        node = edges.pop(0)
        smt2 = translation+"/branch_"+node+".smt2"
        print(path.exists(smt2))
        if path.exists(smt2):
            cmd = "./abc -i" + smt2 +"-v 0"
            out, err = shell.runcmd(cmd)                    #run ABC
            results = get_abc_result_line(out,err)          
            pr = results["count"]/(2**results["bound"])     #Probability
            markov[node] = {edges[0]: pr, edges[1]: 1.0-pr}
            last_state = max(last_state, int(edges[0]), int(edges[1]))
        elif len(edges) != 0:
            markov[node] = {edges[0]:1.0}
            last_state = max(last_state, int(edges[0]))
                                                                                                                                                                                                                    
#Courtesy of the VLab
def get_abc_result_line(out, err):
    lines = err.strip(' \t\n\r,').split('\n')
    var_results = {}
    results = {}
    for line in lines:
        match = re.match(r".*report is_sat:\s*(?P<is_sat>\w+)\s*time:\s*(?P<time>\d+(\.\d+)*)\s*ms\s*", line, re.IGNORECASE)
        if match:
            results["is_sat"] = match.group('is_sat')
            results["solve_time"] = match.group('time')
            continue
        match = re.match(r".*report \(TUPLE\) bound:\s*(?P<bound>\d+)\s*count:\s*(?P<count>\d+)\s*time:\s*(?P<time>\d+(\.\d+)*)\s*ms\s*", line, re.IGNORECASE)
        if match:
            results["bound"] = match.group('bound')
            results["count"] = match.group('count')
            results["count_time"] = match.group('time')
        match = re.match(r".*report bound:\s*(?P<bound>\d+)\s*count:\s*(?P<count>\d+)\s*time:\s*(?P<time>\d+(\.\d+)*)\s*ms\s*", line, re.IGNORECASE)
        if match:
            if "var" in results:
                var_results[results["var"]] = {"bound": match.group('bound'), "count": match.group('count'),     "count_time": match.group('time')}
                continue
        match = re.match(r".*report var:\s*(?P<var>.+)\s*", line, re.IGNORECASE)
        if match:
            results["var"] = match.group('var')
            continue
        results["var"] = var_results
        return results
def format_prism():             #write to a file suitable for PRISM
    global markov
    global last_state
    var = "x"
    rate = 100
    prism = open("prism.pm","w")
    prism.write("dtmc\n\n")
    prism.write("module M1\n\n")
    prism.write(var + ": [0.." + str(last_state) + "] init 0;\n\n")
    print(markov)
    for node, vals in markov.items():
        print(vals)
        firstw = True
        expr = "[] "+ var + "=" + node + " -> "
        for branch in vals:
            if firstw:
                firstw = False
            else:
                expr += " + "
            expr += str(markov[node][branch]*rate) + ":(" + var + "\'=" + branch + ")"
        expr += ";\n"
        prism.write(expr)
    prism.write("\nendmodule")
    prism.close()
#MAIN
if __name__ == "__main__":
    parser = ap.ArgumentParser(description = 'Transforms Control Flow Graph into a DTMC format accepted by PRISM')
    parser.add_argument('-d', '--dir', help = 'Directory of cfg, branches, and translations dir', required = True)
    args = parser.parse_args()
    parse(args.dir+"/cfg",args.dir+"/branches",args.dir+"/translation")
    format_prism()
