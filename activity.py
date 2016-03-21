import datetime
class Activity:
    def __init__(
            self,
            name,
            durationInMinutes,
            pricePerPerson,
            flatPrice = 0,
            childreduction= 0
        ):
        self.name = name
        self.duration = datetime.timedelta(minutes = durationInMinutes)
        self.pricePerPerson = pricePerPerson
        self.flatPrice = flatPrice
        self.childfactor = 1 - childreduction

    def __str__(self):
        return self.name

import inputs
class ActivityManager:
    def __init__(self):
        self.currentActivities = []
        nothing = Activity("niks", 0, 0)
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
                Activity("Borellen", 60, 0.8),
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
            "Eten": [
                Activity("Drentse Broodmaaltijd", 90, 13.9, childreduction=.25),
            ],
            "Ter afsluiting": [
                Activity("Koffie", 30, 2.2),
                Activity("Broodje ham/kaas", 0, 2.5),
            ]
        }
        self._onlyStart = set(["Beginnen met"])

    def getCategories(self):
        keys = self.possibleActivities.keys()
        if self.currentActivities == []:
            return self._onlyStart
        return keys - self._onlyStart
    def planning(self):
        print("")
        print("Start de planning")
        done = "Klaar met planning en ga verder"
        while True:
            self.printCurrentPlanning()
            categories = self.getCategories()
            if len(categories) == 1:
                self.selectActivity(next(iter(categories)))
                continue
            categories.add(done)
            choice = inputs.userChoice("kies optie", categories)
            if choice == done:
                break
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
        result = "\\begin{tabular}{llll} \n"
        for activity in self.currentActivities:

            result += "%s & %s \\\\\n" % (timestr, activity)
        result += "\n \\end{tabular} \n"



