#!/usr/bin/python
import re

fli = open('offer.tex', 'r')
for line in fli:
    match = re.findall('((?<=\$)[A-Z]+)+', line)
    for var in match:
        print(var)

    print(line)
