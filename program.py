#!/usr/bin/python
import re
import os
from subprocess import check_output, CalledProcessError, TimeoutExpired


symbolTable = {}
newFile = []
with open('offer.tex', 'r') as templateFile:
    for line in templateFile:
        match = re.findall('((?<=\$)[A-Z]+)+', line)
        for var in match:
            if var not in symbolTable:
                symbolTable[var] = input("please specify %s \n" % var)
            value = symbolTable[var]
            line = line.replace('\\$'+var,value)

        newFile.append(line)

name = "NAAM"
if symbolTable[name] == "":
    print("Waarschuwing geen bestands naam!")
outPath = "out"
if not os.path.exists(outPath):
    os.makedirs(outPath)
    import shutil
    imgfolder = "img"
    shutil.copytree(imgfolder,"{}/{}".format(outPath,imgfolder))

outFileName = '{}.tex'.format(symbolTable[name])
outFile = '{}/{}'.format(outPath, outFileName)
with open(outFile, 'w') as outputFile:
    print("starting with writing")
    for line in newFile:
        print(line)
        outputFile.write(line)

def executeAction(command):
    print("executing %s" % ' '.join(command))
    result = "" 
    try:
        result = check_output(command, timeout=5, cwd=outPath)
    except CalledProcessError as e: 
        result = e.output
    except TimeoutExpired as e: 
        result = e.output
    print(result.decode("utf8"))

processPdf = [
    "pdflatex",
    "-halt-on-error",
    "-shell-escape",
    outFileName
]
executeAction(processPdf)

# cleanup latex bullshit
os.remove('{}/{}.log'.format(outPath, symbolTable[name]))
os.remove('{}/{}.aux'.format(outPath, symbolTable[name]))
