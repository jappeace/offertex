#!/usr/bin/python
import re
import os
from subprocess import check_output, CalledProcessError, TimeoutExpired


symbolTable = {}
newFile = []

variablesFolder = "variables" # for input sanitation

def selectMenu(optionsFile, var):
    with open(optionsFile, 'r') as options:
        import inputs
        return inputs.userChoice("selecteer een %s: " % var, options.readlines())

def optionsMenu(optionsFile, var):
    def selectIfHasChildren(item):
        hasChildren = symbolTable["KINDEREN"] != "0"
        if item[0] == "k" and hasChildren:
            return item[:0]+"+"+item[1:]
        else:
            return item
    done = "Klaar"
    def selectOptions(lines):
        def flip(line):
            if line[0] == "-":
                return "+" + line[1:]
            return "-" + line[1:]
        selected = inputs.userChoice("selecteer optioneele %s: " % var, lines)
        if selected == done:
            lines.remove(done)
            filtered = filter(lambda line: line[0] == "+",lines)
            return map(lambda line: parseLine(line[2:]), filtered)
        indx = lines.index(selected)
        lines[indx] = flip(selected)
        return selectOptions(lines)

    def toLatexItemlist(lines):
        result = "\\begin{itemize} \n"
        didstuff = False
        for line in lines:
            didstuff = True
            result += "\t\\item %s \n" % line
        result += "\\end{itemize} \n"

        if not didstuff:
            return ""
        return result

    with open(optionsFile, 'r') as options:
        lines = options.readlines()
        import inputs
        lines = map(selectIfHasChildren, lines)
        lines = list(lines)
        lines.append(done)
        return toLatexItemlist(selectOptions(lines))


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
    testFile = "%s.options" % possibleFile
    if os.path.isfile(testFile):
        return optionsMenu(testFile, var)

    return simpleInput(var)

def activitiesDetailsText(actList):
    result = ""
    print("starting figuring out details...")
    folder = "details"
    if not os.path.isdir(folder):
        print("WARNING, %s folder not found" % folder)

    for act in actList:
        actcontent = ""
        for actFSName in act.filesysNames:
            filename = "%s/%s.tex" % (folder, actFSName)
            if not os.path.isfile(filename):
                print("geen details voor %s" % filename)
                continue

            with open(filename, "r") as detailsfile:
                print("openen van details voor %s" % filename)
                for line in detailsfile:
                    actcontent += line
        if actcontent != "":
            result += "\\subsection*{%s}" % act.name
            result += actcontent

    return result

import activity
manager = activity.ActivityManager()

def parseLine(line):
    match = re.findall('((?<=\$)[A-Z]+)+', line)
    for var in match:
        if var not in symbolTable:
            value = ""
            if var == "STARTPLANNING":
                manager.planning()
                symbolTable["DRAAIBOEK"] = manager.toTimeTableLatexStr(symbolTable["BEGINTIJD"])
                symbolTable["PRIJSOVERZICHT"] = manager.toPriceTableLatexStr(symbolTable["GROEPGROTE"], symbolTable["KINDEREN"])
            elif var == "ACTIVITEITDETAILS":
                value = activitiesDetailsText(manager.currentActivities)

            else:
                value = fillVar(var)
                if value == "":
                    #prevents certain kinds of latex compilation bugs
                    value = "-"
            symbolTable[var] = value
        value = symbolTable[var]
        line = line.replace('\\$'+var,value)
    return line

with open('offer.tex', 'r') as templateFile:
    for line in templateFile:
        newFile.append(parseLine(line))

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
executeAction(processPdf) # twice for background?

# cleanup latex bullshit
os.remove('{}/{}.log'.format(outPath, symbolTable[name]))
os.remove('{}/{}.aux'.format(outPath, symbolTable[name]))
