import os
import sys

f = open("libxml2-taint-analysis.txt", "r")
content = f.read()
lineNumbers = content.split(" ")

updated_content = ""
for line in lineNumbers:
  l = int(line)
  if l >= 10744:
    updated_content += str(l+20) + " "
  else:
    updated_content += str(l+11) + " "

fw = open("libxml2-taint-analysis-updated.txt", "w")
fw.write(updated_content)