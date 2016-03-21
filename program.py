#!/usr/bin/python
import re
import os
from subprocess import check_output, CalledProcessError, TimeoutExpired


symbolTable = {}
newFile = []

variablesFolder = "variables" # for input sanitation

def selectMenu(optionsFile, var):
    with open(optionsFile, 'r') as options:
        print("%s has a set of choices: " % var)
        optmap = {}
        for n,line in enumerate(options):
            optmap[n] = line
            print("%d: %s" % (n,line), end="")
        try:
            selected = int(input("your choice: \n"))
        except ValueError:
            print("invalid input try again")
            return selectMenu(optionsFile, var)
        return optmap[selected]

def regexMatchInput(testFile, var):
    with open(testFile, "r") as tfile:
        regex = tfile.readline()
        failmsg = tfile.readline()
        userInput = simpleInput(var)
        if re.match(regex.rstrip(), userInput) is None:
            print(failmsg % var)
            return regexMatchInput(testFile, var)
        return userInput

def simpleInput(var):
    return input("please specify %s \n" % var)
def fillVar(var):
    possibleFile = "{}/{}".format(variablesFolder,var.lower())
    testFile = "%s.select" % possibleFile
    if os.path.isfile(testFile):
        return selectMenu(testFile, var)
    testFile = "%s.constraint" % possibleFile
    if os.path.isfile(testFile):
        return regexMatchInput(testFile, var)
    return simpleInput(var)
with open('offer.tex', 'r') as templateFile:
    for line in templateFile:
        match = re.findall('((?<=\$)[A-Z]+)+', line)
        for var in match:
            if var not in symbolTable:
                value = fillVar(var)
                if value == "":
                    value = "notset" #prevents certain kinds of latex compilation bugs
                symbolTable[var] = value
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
        print(line, end="")
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
