#!/usr/bin/python
# This program parses the offer.tex file to produce a copy where the variables are filled in.
# Copyright (C) 2016 Jappe Klooster

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.If not, see <http://www.gnu.org/licenses/>.


import re
import os
import inputs

print("Offertex Copyright (C) 2016 Jappie Klooster")
print("This program comes with ABSOLUTELY NO WARRANTY; for details see the")
print("LICENSE file. This is free software, and you are welcome to ")
print("redistribute it under certain conditions; see the LICENSE file for details")
print("")
print("")

# move to the current directory so we can find the offer.tex file
# (required for qpython as it starts in root, also just makes
# the script more robust).
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

os.chdir("user")
choices = [directory for directory in os.listdir() if os.path.isdir(directory)]
os.chdir(inputs.userChoice("Choose user", choices))

symbolTable = {}
newFile = []

variablesFolder = "variables" # for input sanitation


def selectMenu(optionsFile, var):
    with open(optionsFile, 'r') as options:
        return parseLine(
            inputs.userChoice("selecteer een %s: " % var, options.readlines())
        )

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
            # remove the done option
            lines.remove(done)
            # filter selected items
            filtered = filter(lambda line: line[0] == "+",lines)
            # remove the selection symbol
            # parse for user choice ($ anotated strings)
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
    return input("specificeer %s \n" % var)

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

import activity
manager = activity.ActivityManager.createFromFileSystem()

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
                value = manager.activitiesDetailsText()

            else:
                value = fillVar(var)
                if value == "":
                    #prevents certain kinds of latex compilation bugs
                    value = "-"
            symbolTable[var] = value
        value = symbolTable[var]
        line = line.replace('\\$'+var,value)
    return line

templatesFolder = "templates"
if not os.path.isdir(templatesFolder):
    raise OSError("%s folder not found"% templatesFolder)
onlyfolders = [d for d in os.listdir(templatesFolder) if os.path.isdir(os.path.join(templatesFolder, d))]
selected = inputs.userChoice("Selecteer een template", onlyfolders)
with open(os.path.join(templatesFolder, selected, 'offer.tex'), 'r') as templateFile:
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
    shutil.copytree(imgfolder,"%s/%s" % (outPath,imgfolder))

outFileName = symbolTable[name]
outFileName = outFileName.replace(".", "")
outFileName = outFileName.replace("/", "")
outFileName = outFileName.replace(" ", "")
attempts = ""

def createOutfile(name,attempts):
    if not attempts == "":
        attempts = "(%s)" % attempts
    return '%s%s.tex' % (outFileName,attempts)
def createOutFileName(path, name, attempts):
    return '%s/%s' % (path,createOutfile(outFileName,attempts))

while os.path.isfile(createOutFileName(outPath, outFileName,attempts)):
    attempts += "I"

outFile = createOutFileName(outPath, outFileName,attempts)
outFileName = createOutfile(outFileName, attempts) # adminastration

with open(outFile, 'w') as outputFile:
    print("starting with writing")
    for line in newFile:
        print(line, end="")
        outputFile.write(line)
