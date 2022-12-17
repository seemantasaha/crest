def main(branchConstraintDir):
    branchesPath = branchConstraintDir + "/" + "branch_statements"
    branchesFile = open(branchesPath, 'r')
    lines = branchesFile.readlines()
    log = ""

    xsltLineSet = set()
    xsltFile = open("/home/seem/Research/libxslt-cil/libxslt/xslt.c", "r")
    xsltLines = xsltFile.readlines()
    lineno = 1
    for xsltLine in xsltLines:
        if "xmlStrEqual" in xsltLine or "IS_XSLT_ELEM" in xsltLine or "IS_XSLT_NAME" in xsltLine:
            xsltLineSet.add(str(lineno))
        lineno += 1
    
    print(xsltLineSet)

    for line in lines:
        if line.startswith("tmp"):
            lineInfo = line.split(", ")

            if "xslt.c" in lineInfo[5]:
                log += str(lineInfo[5]) + "\n"
                line_num = lineInfo[5].split(":")[1]
                print(line_num)
                if line_num in xsltLineSet:
                    countFilePath = "model_counts/branch_" + lineInfo[1] + ".count"
                    countFile = open(countFilePath, "w")
                    countFile.write("1,4294967296,False")
                    countFile.close()

    branchesFile.close()
    
    linesFilePath = "lineToModel.txt" 
    linesFile = open(linesFilePath, "w")
    linesFile.write(log)
    linesFile.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Provide the directory for branch consraints...')
    parser.add_argument('--branch_constraints_dir', metavar='dir', required=True,
                        help='path to the directory of all branch constraints')
    args = parser.parse_args()
    main(branchConstraintDir=args.branch_constraints_dir)