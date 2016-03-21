
class Activity:
    def __init__(self, naam, duratie, prijs):
        self.naam = naam
        self.duratie = duratie
        self.prijs = prijs

    def __str__(self):
        return self.naam

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
            ]
        }
        self._onlyStart = set(["Beginnen met"])

    def getCategories(self):
        keys = self.possibleActivities.keys()
        if self.currentActivities == []:
            return self._onlyStart
        return keys - self._onlyStart
    def planning(self):
        print()
        print("Starting planning")
        done = "Klaar"
        while True:
            categories = self.getCategories()
            if len(categories) == 1:
                self.selectActivity(next(iter(categories)))
                continue
            categories.append(done)
            choice = inputs.userChoice("select category", categories)
            if choice == done:
                break
            self.selectActivity(choice)
            print(self.currentActivities)

    def selectActivity(self, category):
        items = self.possibleActivities[category]
        choice = inputs.userChoice("select a %s activity" % category, items)
        self.currentActivities.append(choice)
