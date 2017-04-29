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


import os
import shutil
from collections import namedtuple

import inputs
import activity
import parse


outPath = "out"
templatesFolder = "templates"
templatefile = 'offer.tex'

NewFile = namedtuple('NewFile', ['name', 'path'])

def askUserTemplate():
    """Ask the user which template to use"""
    if not os.path.isdir(templatesFolder):
        raise OSError("%s folder not found"% templatesFolder)
    onlyfolders = [
        d for d in os.listdir(templatesFolder)
        if os.path.isdir(os.path.join(templatesFolder, d))
    ]
    selected = inputs.userChoice("Selecteer een template", onlyfolders)
    return NewFile(templatefile, os.path.join(templatesFolder, selected))

def readTemplateAndWriteResult():
    """Read the template file and write the template result in out dir"""
    # move to the current directory so we can find the offer.tex file
    # (required for qpython as it starts in root, also just makes
    # the script more robust).
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)

    os.chdir("user")
    choices = [directory for directory in os.listdir() if os.path.isdir(directory)]
    os.chdir(inputs.userChoice("Choose user", choices))

    parser = parse.UserInterface(
        activity.ActivityManager.createFromFileSystem()
    )
    parsedFile = parser.parseFile(askUserTemplate())

    if parsedFile.filename == "":
        print("Waarschuwing geen bestands naam!")
    if not os.path.exists(outPath):
        os.makedirs(outPath)
        imgfolder = "img"
        shutil.copytree(imgfolder, "%s/%s" % (outPath, imgfolder))

    writer = NameWriter()
    sanatized = NameWriter.sanatize(parsedFile.filename)

    out = writer.findValidOutName(outPath, sanatized)

    with open(out.path, 'w') as outputFile:
        print("starting with writing")
        outputFile.write(parsedFile.content)

    return out

class NameWriter:
    """Finds a free file name (with roman numerals)"""
    _initialAttempts = ""
    def __init__(self):
        self.attempts = NameWriter._initialAttempts

    @staticmethod
    def sanatize(name, withWhat = "", toReplace = [".", "/", " "]):
        """removes crazy stuff from filenames"""
        for replace in toReplace:
            name = name.replace(replace, withWhat)
        return name

    def _createOutName(self, name):
        """Creates the final file name with the numerals"""
        # copy so we don't overwrite
        attempts = self.attempts
        if attempts != NameWriter._initialAttempts:
            attempts = "(%s)" % self.attempts.replace("IIIII", "V").replace("VV", "X")
        return '%s%s.tex' % (name, attempts)

    def _createOutPath(self, path, name):
        """Creates the filename as a path"""
        return '%s/%s' % (path, self._createOutName(name))

    def findValidOutName(self, path, name):
        """Keeps increasing attempts until it found a valid name"""
        while os.path.isfile(self._createOutPath(path, name)):
            self.attempts += "I"
        result = NewFile(
            self._createOutName(name),
            self._createOutPath(path, name)
        )
        self.attempts = NameWriter._initialAttempts
        return result
