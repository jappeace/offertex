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
from android import outFileName, outPath, symbolTable, name
from subprocess import check_output, CalledProcessError, TimeoutExpired

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

input("done, output can be found in %s, press enter to exit program" % outPath)
