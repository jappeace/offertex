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
from collections import namedtuple

import inputs

_variablesFolder = "variables" # for input sanitation

fileNameSymbol = "NAAM"
ParseResult = namedtuple('ParseResult', ['filename', 'content'])

class UserInterface:
    """does the user interface and parsing"""

    initSymbolTable = {}
    def __init__(self, manager):
        self.manager = manager
        self.symbolTable = UserInterface.initSymbolTable

    def selectMenu(self, optionsFile, var):
        with open(optionsFile, 'r') as options:
            return self.parseLine(
                inputs.userChoice("selecteer een %s: " % var, options.readlines())
            )

    def optionsMenu(self, optionsFile, var):
        def selectIfHasChildren(item):
            hasChildren = self.symbolTable["KINDEREN"] != "0"
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
                return map(lambda line: self.parseLine(line[2:]), filtered)
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

    def regexMatchInput(self, testFile, var):
        with open(testFile, "r") as tfile:
            regex = tfile.readline()
            failmsg = tfile.readline()
            userInput = inputs.simpleInput(var)
            if re.match(regex.rstrip(), userInput) is None:
                print(failmsg % var)
                return self.regexMatchInput(testFile, var)
            return userInput


    def fillVar(self, var):
        possibleFile = "{}/{}".format(_variablesFolder,var.lower())
        testFile = "%s.select" % possibleFile
        if os.path.isfile(testFile):
            return self.selectMenu(testFile, var)
        testFile = "%s.constraint" % possibleFile
        if os.path.isfile(testFile):
            return self.regexMatchInput(testFile, var)
        testFile = "%s.options" % possibleFile
        if os.path.isfile(testFile):
            return self.optionsMenu(testFile, var)

        return inputs.simpleInput(var)

    def parseLine(self, line):
        match = re.findall('((?<=\$)[A-Z]+)+', line)
        for var in match:
            if var not in self.symbolTable:
                value = ""
                if var == "STARTPLANNING":
                    begintijd = self.symbolTable["BEGINTIJD"]
                    self.manager.planning(begintijd )
                    self.symbolTable["DRAAIBOEK"] = self.manager.toTimeTableLatexStr(begintijd )
                    self.symbolTable["PRIJSOVERZICHT"] = self.manager.toPriceTableLatexStr(self.symbolTable["GROEPGROTE"], self.symbolTable["KINDEREN"])
                elif var == "ACTIVITEITDETAILS":
                    value = self.manager.activitiesDetailsText()

                else:
                    value = self.fillVar(var)
                    if value == "":
                        #prevents certain kinds of latex compilation bugs
                        value = "-"
                self.symbolTable[var] = value
            value = self.symbolTable[var]
            line = line.replace('\\$'+var,value)
        return line

    def parseFile(self, templatename):
        newFile = []
        with open(templatename, 'r') as templateFile:
            for line in templateFile:
                newFile.append(self.parseLine(line))
        result = ParseResult(self.symbolTable[fileNameSymbol], newFile)

        self.symbolTable = UserInterface.initSymbolTable
        return result
