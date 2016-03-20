#!/usr/bin/python
import re

fli = open('offer.tex', 'r')

symbolTable = {}
newFile = []
for line in fli:
    match = re.findall('((?<=\$)[A-Z]+)+', line)
    for var in match:
        if var not in symbolTable:
            symbolTable[var] = input("please specify %s \n" % var)
        value = symbolTable[var]
        line = line.replace('\\$'+var,value)

    newFile.append(line)

for line in newFile:
    print(line)
