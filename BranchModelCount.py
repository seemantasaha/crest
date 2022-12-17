import sys
import os
import subprocess

def modelCount(consPath):
		print(consPath)
		process = subprocess.Popen(["abc", "-i", consPath, "-bi", "15", "-v", "0"], stdout = subprocess.PIPE)
		result = process.communicate()[0].decode('utf-8')
		#process.terminate()
		print(result)
		lines = result.split('\n');
		print(lines)
		count = 0
		flag = False
		if lines[0] == "sat":
			count = int(lines[1])
		else:
			flag = True
		return (count, flag)

def computeDomain(consPath):
		intDomainSize = 1
		consFile = open(consPath, 'r')
		lines = consFile.readlines()
		for line in lines:
			if "(assert (and (>= " in line and " 0) (<= " in line and " 255)))" in line:
				intDomainSize *= 256
			elif "(assert (and (>= " in line and " (- 128))) (<= " in line and " 127)))" in line:
				intDomainSize *= 256
			elif "(assert (and (>= " in line and " 0)) (<= " in line and " 1)))" in line:
				intDomainSize *= 2
			elif "(assert (and (>= " in line and " 0)) (<= " in line and " 32767)))" in line:
				intDomainSize *= 2**15
			elif "(assert (and (>= " in line and " (- 32768)) (<= " in line and " 32767)))" in line:
				intDomainSize *= 2*(2**15)
			#else:
			#	intDomainSize *= 2*(2**15)
		#print("Domain size for this constraint is: " + str(intDomainSize))
		return intDomainSize

def main(branchConstraintDir):
    for filename in os.listdir(branchConstraintDir):
        if not filename.endswith("smt2"):
            continue
        branchid = int(filename.split("_")[1].split(".smt2")[0])
        if not ((branchid >= 374556 and branchid <= 377494) or (branchid >= 394898 and branchid <= 397323) or (branchid >= 397614 and branchid <= 402026)):
            continue
        consPath = branchConstraintDir + "/" + filename
        count, flag = modelCount(consPath)
        domain = computeDomain(consPath)
        countPath = consPath.replace("smt2", "count")
        f = open(countPath, "w")
        f.write(str(count)+","+str(domain)+","+str(flag))
        f.close()



if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Provide the directory for branch consraints...')
    parser.add_argument('--branch_constraints_dir', metavar='dir', required=True,
                        help='path to the directory of all branch constraints')
    args = parser.parse_args()
    main(branchConstraintDir=args.branch_constraints_dir)
