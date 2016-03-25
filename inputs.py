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


def userChoice(msg, options):
    print(msg)
    optmap = {}
    for n,line in enumerate(options):
        optmap[n] = line
        print("%d: %s" % (n,str(line).rstrip()))
    try:
        selected = int(input("Uw keuze: \n"))
    except ValueError:
        print("Ongeldige invoer, ik acepteer alleen maar integers")
        return userChoice(msg, options)
    if selected in optmap:
        return optmap[selected]
    else:
        print("%d is niet beschikbaar als keuze" % selected)
        return userChoice(msg, options)

# try again on value error
def intput(msg):
    while True:
        try:
            return int(input(msg))
        except ValueError:
            print("Acepteer alleen integers")
