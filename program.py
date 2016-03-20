#!/usr/bin/python
import re
import os



symbolTable = {}
newFile = []
for line in open('offer.tex', 'r'):
    match = re.findall('((?<=\$)[A-Z]+)+', line)
    for var in match:
        if var not in symbolTable:
            symbolTable[var] = input("please specify %s \n" % var)
        value = symbolTable[var]
        line = line.replace('\\$'+var,value)

    newFile.append(line)

name = "NAME"
outPath = "out"
if not os.path.exists(outPath):
    os.makedirs(outPath)

outputFile = open('{}/{}.tex'.format(outPath, symbolTable[name]), 'w')
for line in newFile:
    outputFile.write(line)
