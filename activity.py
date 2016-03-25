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


import datetime
class Activity:
    def __init__(
            self,
            name,
            durationInMinutes,
            pricePerPerson,
            flatPrice = 0,
            childreduction= 0,
            countable = False
        ):
        self.name = name
        self.duration = datetime.timedelta(minutes = durationInMinutes)
        self.pricePerPerson = pricePerPerson
        self.flatPrice = flatPrice
        self.childfactor = 1 - childreduction
        self.filesysNames = [name.lower().replace(" ", "_")]
        self.countable = countable

    def __str__(self):
        return self.name

class Decoration(Activity):
    def __init__(self, base, extension, nameoverwrite = ""):
        if nameoverwrite == "":
            self.name = "%s + %s" % (base.name, extension)
        else:
            self.name = nameoverwrite

        self.duration = base.duration + extension.duration
        self.pricePerPerson = base.pricePerPerson + extension.pricePerPerson
        self.flatPrice = base.flatPrice + extension.flatPrice
        # good luck making a composition out of this...
        # lets use a reducing default strategy instead.
        self.childfactor = extension.childfactor
        if base.childfactor != 1:
            self.childfactor = base.childfactor
        self.filesysNames = base.filesysNames + extension.filesysNames
        self.countable = base.countable or extension.countable

import inputs
class ActivityManager:
    def __init__(self):
        self.currentActivities = []
        nothing = Activity("niks", 0, 0)

        eten = "Eten"
        self.possibleActivities = {
            "Beginnen met": [
                Activity("2x Koffie gebak", 60, 6.9),
                Activity("2x Koffie cake", 60, 5.5),
                Activity("2x Koffie petit", 60, 6.0),
                Activity("1x Koffie", 30, 2.2),
                Activity("1x Koffie compleet", 30, 3.5),
                nothing
            ],
            "Tussen door": [
                Activity("Prosseco", 0, 3.0),
                Activity("Hapjes koud", 0, 0.8),
                Activity("Hapjes koud mix", 0, 1.3),
                Activity("Hapjes warm", 0, 1.3),
                Activity("Hapjes bittergarnituur", 0, 0.8),
                Activity("Consumpties", 0, 2.3, countable = True),
            ],
            "Aktiviteit": [
                Activity("Klootschieten", 75, 2),
                Activity("Oud hollandse spelletjes", 75, 0, 75),
                Activity("Huifkar", 60, 0, 175),
                Activity("Video Quize", 60, 0, 75),
                Activity("Steps", 90, 8),
                Activity("Fietsen", 90, 12),
                Activity("Tandem", 90, 22),
                Activity("Boerengolf", 90, 10),
                Activity("Solex", 120, 30),
                Activity("Tractor puzzel tocht", 120, 30),
                Activity("Spel", 200, 6,150),
            ],
            eten: [
                Activity("Koud, warm en dessert buffet De Huiskamer", 180, 37.9, childreduction=.25),
            ],
            "Ter afsluiting": [
                Activity("Koffie", 30, 2.2),
                Activity("Broodje ham/kaas", 0, 2.5),
            ]
        }
        brood = Activity("Drentse Broodmaaltijd", 90, 13.9, childreduction=.25)
        kroket = Activity("kroket", 0, 2)
        luxeBroodjes = Activity("luxebroodjes", 0, 2)
        brunch_base = Decoration(brood, Decoration(kroket,luxeBroodjes))
        brunch = Activity("Brunch", 30, 7)
        brunch_hk = Activity("Brunch De Huiskamer", 0, 5)
        self.possibleActivities[eten] += [
            brood,
            Decoration(brood, kroket),
            Decoration(brood, luxeBroodjes),
            brunch_base
        ]
        tmp = Decoration(brunch, brunch_base)
        tmp.name = brunch.name
        self.possibleActivities[eten] += [tmp]

        tmp = Decoration(brunch_hk, tmp)
        tmp.name = brunch_hk.name
        self.possibleActivities[eten] += [
                tmp,
                Activity("Hightea De Huiskamer", 120, 22.9, childreduction=.25),
                Activity("Hightea Ansen", 90, 19.5, childreduction=.25),
                Activity("Keuzemenu soep", 150, 32.9),
                Activity("Keuzemenu drie gangen", 150, 37.9),
                Activity("Keuzemenu vier gangen", 180, 42.9),
        ]
        koud = Activity("buffetkoud", 60, 0, childreduction=.25)
        warm = Activity("buffetwarm", 60, 27.9, childreduction=.25)
        dessert = Activity("Buffet dessert", 60, 0, childreduction=.25)
        warmdessert = Decoration(warm, dessert, nameoverwrite="Warm en dessert buffet")
        kwdbuffet = Decoration(koud, warmdessert)
        self.possibleActivities[eten] += [
            Decoration(koud, warm, nameoverwrite="Koud en warm buffet"),
            warmdessert,
            Decoration(Activity("Buffet Ansen", -60, 2), kwdbuffet, nameoverwrite="Buffet Ansen"),
            Decoration(Activity("Buffet De Huiskamer", 0, 10), kwdbuffet, nameoverwrite="Buffet De Huiskamer")
        ]
        # because price inconsisitency...
        dessert = Activity("Buffet dessert", 45, 9.9, childreduction=.25)
        soep = Activity("Buffet soep", 30, 5.9)
        ijs = Activity("Buffet ijs", 30, 5.9)
        self.possibleActivities[eten] += [
            dessert,
            Activity("Barbeque Ansen", 120, 29.9),
            Activity("Barbeque De Huiskamer", 180, 37.9),
            Decoration(soep,
                Decoration(
                    Activity("Buffetwarm goedkoop", 60, 15.1, childreduction=.25), ijs
                ),
                nameoverwrite="Soep, warm en ijs buffet"
            ),
            ijs,
            soep,
            Activity("Buffet pannenkoeken", 60, 12),
            Activity("Lunch", 60, 9.9),
            Activity("Receptie arrangement", 240, 28.5),
        ]
        self._onlyStart = set(["Beginnen met"])

    def getCategories(self):
        keys = self.possibleActivities.keys()
        if self.currentActivities == []:
            return sorted(list(self._onlyStart))
        return sorted(list(keys - self._onlyStart))
    def planning(self):
        print("")
        print("Start de planning")
        delete = "Verwijder laatste toevoeging"
        done = "Klaar met planning en ga verder"
        while True:
            self.printCurrentPlanning()
            categories = self.getCategories()
            if len(categories) == 1:
                self.selectActivity(next(iter(categories)))
                continue
            categories.append(done)
            categories.append(delete)
            choice = inputs.userChoice("kies optie", categories)
            if choice == done:
                break
            if choice == delete:
                self.currentActivities.pop()
                continue
            self.selectActivity(choice)

    def selectActivity(self, category):
        items = self.possibleActivities[category]
        choice = inputs.userChoice("selecteer een %s activiteit" % category, items)
        self.currentActivities.append(choice)

    def printCurrentPlanning(self):
        print("")
        print("---")
        if len(self.currentActivities) > 0:
            print("Huidige planning")
        for i,activity in enumerate(self.currentActivities):
            print("%d: %s"%(i,activity))
        print("")

    def toTimeTableLatexStr(self, startingTime):
        currentTime = datetime.datetime.strptime(startingTime, "%H:%M")
        result = "\\begin{tabular}{ll} \n"
        for activity in self.currentActivities:
            timestr = currentTime.strftime("%H.%M uur")
            result += "%s & %s \\\\\n" % (timestr, activity)
            currentTime += activity.duration
        result += "%s & %s \\\\\n" % (currentTime.strftime("%H.%M uur"), "Einde")
        result += "\n \\end{tabular} \n"
        return result
    def toPriceTableLatexStr(self, peopleCount, childrenCount):
        result = "\\begin{tabular}{l l l r l r} \n"
        totalPrice = 0
        childrenCount = int(childrenCount)
        peopleCount = int(peopleCount)

        for activity in self.currentActivities:
            adults = peopleCount
            if activity.countable:
                trying = True
                while trying:
                    try:
                        adults = adults * int(input("hoeveel %s?\n" % activity.name))
                        trying = False
                    except ValueError:
                        print("invalid input")

            if childrenCount != 0 and activity.childfactor != 1:
                adults -= childrenCount

            if activity.pricePerPerson != 0:
                perPersonCosts = activity.pricePerPerson * adults
                totalPrice += perPersonCosts
                result += "%d & %s & \\euro{} & %.2f & \\euro{} & %.2f \\\\\n" % \
                (adults, activity, activity.pricePerPerson, perPersonCosts)

            if peopleCount != adults:
                childprice = activity.pricePerPerson * activity.childfactor
                childCost = childrenCount*childprice
                result += "%d & Kinderen & \\euro{} & %.2f & \\euro{} & %.2f \\\\\n" % \
                (childrenCount, childprice, childCost)
                totalPrice += childCost

            if activity.flatPrice != 0:
                result += "1 & %s & \\euro{} & %.2f & \\euro{} & %.2f \\\\\n" % \
                (activity, activity.flatPrice, activity.flatPrice)
                totalPrice += activity.flatPrice

        result += "\\hline\n"
        result += "& Totaal incl. btw & & & \\euro{} & %.2f \\\\\n" % totalPrice
        result += "\\end{tabular} \n"
        return result
