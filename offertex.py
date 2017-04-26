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

import activity
import parse

from collections import namedtuple

outPath = "out"
NewFile = namedtuple('NewFile', ['name', 'path'])

def main():
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

    newFile = []
    manager = activity.ActivityManager.createFromFileSystem()
    parser = parse.UserInterface(manager)

    templatesFolder = "templates"
    if not os.path.isdir(templatesFolder):
        raise OSError("%s folder not found"% templatesFolder)
    onlyfolders = [d for d in os.listdir(templatesFolder) if os.path.isdir(os.path.join(templatesFolder, d))]
    selected = inputs.userChoice("Selecteer een template", onlyfolders)
    with open(os.path.join(templatesFolder, selected, 'offer.tex'), 'r') as templateFile:
        for line in templateFile:
            newFile.append(parser.parseLine(line))

    name = "NAAM"
    if parser.symbolTable[name] == "":
        print("Waarschuwing geen bestands naam!")
    if not os.path.exists(outPath):
        os.makedirs(outPath)
        import shutil
        imgfolder = "img"
        shutil.copytree(imgfolder,"%s/%s" % (outPath,imgfolder))

    outFileName = parser.symbolTable[name]
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

    return NewFile(outFileName, outFile)
