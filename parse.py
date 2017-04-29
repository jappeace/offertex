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

import jinja2 as jin
import jinmeta as meta

import inputs

_variablesFolder = "variables" # for input sanitation

fileNameSymbol = "naam"
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
            hasChildren = self.symbolTable["kinderen"] != "0"
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
        if var in self.symbolTable:
            return self.symbolTable[var]

        #TODO this shoulnd't be done here, move to varfolder somehow
        if var == "startplanning":
            begintijd = self.symbolTable["begintijd"]
            self.manager.planning(begintijd )
            self.symbolTable["draaiboek"] = self.manager.toTimeTableLatexStr(begintijd)
            self.symbolTable["prijsoverzicht"] = self.manager.toPriceTableLatexStr(self.symbolTable["groepgrote"], self.symbolTable["kinderen"])
            return ""
        #TODO this shoulnd't be done here, move to varfolder somehow
        if var == "activiteitdetails":
            return self.manager.activitiesDetailsText()

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
            value = self.fillVar(var)
            self.symbolTable[var] = "-" if value == "" else value
            line = line.replace('\\$'+var, self.symbolTable[var])
        return line

    LATEX_SUBS = [
        (re.compile(r'\\'), r'\\textbackslash'),
        (re.compile(r'([{}_#%&$])'), r'\\\1'),
        (re.compile(r'~'), r'\~{}'),
        (re.compile(r'\^'), r'\^{}'),
        (re.compile(r'"'), r"''"),
        (re.compile(r'\.\.\.+'), r'\\ldots'),
    ]

    @staticmethod
    def escape_tex(value):
        newval = value
        for pattern, replacement in UserInterface.LATEX_SUBS:
            newval = pattern.sub(replacement, newval)
        return newval
    @staticmethod
    def createEnvironment(path):
        texenv = jin.Environment(
            loader=jin.FileSystemLoader(path),
            enable_async=False
        )
        texenv.block_start_string = '<='
        texenv.block_end_string = '=>'
        texenv.variable_start_string = '<?'
        texenv.variable_end_string = '?>'
        texenv.comment_start_string = '<!--'
        texenv.comment_end_string = '-->'
        texenv.filters['escape_tex'] = UserInterface.escape_tex
        return texenv

    def parseFile(self, templateinfo):
        environment = UserInterface.createEnvironment(templateinfo.path)
        template_source = environment.loader.get_source(environment,   templateinfo.name)[0]
        parsed_content = environment.parse(template_source)
        undecleared = meta.filter_out_built_ins(
            meta.find_undeclared_variables_in_order(parsed_content)
        )
            

        for var in undecleared:
            self.symbolTable[var] = self.fillVar(var)
        
        template = environment.get_template(templateinfo.name)
        result = template.render(self.symbolTable)
        return ParseResult(
            self.symbolTable[fileNameSymbol],
            result
        )
