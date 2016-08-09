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
import inputs
import os
import re
import json
class Activity:
    default_name = "default"
    use_group_size = -1
    def __init__(self):
        self.name = Activity.default_name
        self.duration_minutes = 0
        self.price_pp_euros = 0
        self.price_flat_euros = 0
        self.childreduction_pp_euros = 0
        self.custom_people_count = Activity.use_group_size
        self.detail_files =  []
    def __str__(self):
        result = self.name
        if self.custom_people_count != Activity.use_group_size:
            result = "%ix %s" % (self.custom_people_count, self.name)
        return result
    def __repr__(self):
        return self.name
    def create_from_file(filename):
        result = Activity()
        with open(filename,'r') as data:
            son = "".join(data.readlines())
            print(son)
            obj = json.loads(son)
            for key in result.__dict__.keys():
                if key in obj:
                    result.__dict__[key] = obj[key]
            if result.name == Activity.default_name:
                result.name = filename.replace(".json", "").replace("_", " ").title()

            return result
        raise ValueError("Could not open %s" % filename)
    def ask_custom_people_count(self):
        self.custom_people_count = inputs.intput(
            "Hoeveel mensen? %i voor gebruik groepgrote" % Activity.use_group_size
        )

class ActivityManager:

    def readdefaults():
        with open("default.json", "r") as deffile:
            return "".join(deffile.readlines())
        raise ValueError("couldn't read defaults")
    def createFromFileSystem():
        result = ActivityManager()
        os.chdir("activities")

        reg = re.compile("\.json$")
        for directory in [d for d in os.listdir() if os.path.isdir(d)]:
            cat_key = directory.split('_',1)[-1].title().replace('_', ' ')
            os.chdir(directory)
            result.possible_activities[cat_key] = [
                Activity.create_from_file(fi) for fi in os.listdir() if reg.search(fi) and os.path.isfile(fi)
            ]
            os.chdir("../")

        with open("config.json") as configfile:
            config = json.loads("".join(configfile.readlines()))
            result.only_on_start = config["only_on_start"]

        os.chdir("../")
        return result

    def __init__(self):
        self.current_activities = []
        self.only_on_start = []
        self.possible_activities = {}
        self.first_execution = True 

    def getCategories(self):
        keys = self.possible_activities.keys()
        if self.first_execution:
            self.first_execution = False
            return sorted(list(self.only_on_start))
        return sorted(list(keys - self.only_on_start))
    def planning(self):
        print("")
        print("Start de planning")

        run_menu_loop = True
        def disable_loop():
            nonlocal run_menu_loop 
            run_menu_loop = False
        def own_field():
            result = Activity()
            print("Maak tijdelijk eigen veld, voor permanent gelieve een bestand aanmaken in user/username/activities")
            result.name = inputs.intput_str("Naam")
            result.price_pp_euros = inputs.intput_float("Prijs per persoon, in euros")
            result.price_flat_euros = inputs.intput_float("Prijs, extra, ongeacht persoon aantal, in euros")
            if result.price_pp_euros != 0:
                result.childreduction_pp_euros = 1-inputs.intput_float("Kinder korting, in procenten") / 100
            result.ask_custom_people_count()
            self.current_activities.append(result)
        def edit_peoplecount():
            choice = inputs.userChoice("Which activity", self.current_activities)
            choice.ask_custom_people_count()
        special_operations = {
            "Verwijder laatste toevoeging": lambda: self.current_activities.pop(),
            "Klaar met planning en ga verder": disable_loop,
            "Voeg eigen veld toe": own_field,
            "Bewerk aantal personen van veld": edit_peoplecount
        }
        while run_menu_loop:
            self.printCurrentPlanning()
            categories = self.getCategories()
            if len(categories) == 1:
                self.selectActivity(next(iter(categories)))
                continue
            categories.extend(special_operations.keys())
            choice = inputs.userChoice("kies optie", categories)
            if choice in special_operations.keys():
                special_operations[choice]()
                continue
            self.selectActivity(choice)

    def selectActivity(self, category):
        items = list(self.possible_activities[category])
        go_back = "Terug"
        items.append(go_back)
        choice = inputs.userChoice("selecteer een %s activiteit" % category, items)
        if choice != go_back:
            self.current_activities.append(choice)

    def printCurrentPlanning(self):
        print("")
        print("---")
        if len(self.current_activities) > 0:
            print("Huidige planning")
        for i,activity in enumerate(self.current_activities):
            print("%d: %s"%(i,activity))
        print("")


    def toTimeTableLatexStr(self, startingTime):
        currentTime = datetime.datetime.strptime(startingTime, "%H:%M")
        result = "\\begin{tabular}{ll} \n"
        for activity in self.current_activities:
            if activity.configureable:
                activity.setDuration(inputs.intput("hoelang %s in minuten?\n" % activity.name))
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

        for activity in self.current_activities:
            adults = peopleCount
            if activity.configureable:
                adults = adults * inputs.intput("hoeveel %s per persoon?\n" % activity.name)

            if childrenCount != 0 and activity.childfactor != 1:
                adults -= childrenCount

            if activity.pricePerPerson != 0:
                perPersonCosts = activity.pricePerPerson * adults
                totalPrice += perPersonCosts
                result += "%d & %s & \\euro{} & %.2f & \\euro{} & %.2f \\\\\n" % \
                (adults, activity, activity.pricePerPerson, perPersonCosts)

            if peopleCount != adults and not activity.configureable:
                # doulbe rounding is a big no no, but the offer should look
                # nice, and having individual cents on it just makes it look
                # greedy.
                # The only way to do this right is by doing double roundings
                # because we don't want people recalulating and have a difference
                # of several euros.
                childprice = round(activity.pricePerPerson * activity.childfactor, 1)
                childCost = round(childrenCount*childprice,1)
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

    def activitiesDetailsText(self):
        result = ""
        print("starting figuring out details...")
        folder = "details"
        import os
        if not os.path.isdir(folder):
            print("WARNING, %s folder not found" % folder)

        for act in self.current_activities:
            actcontent = ""
            for actFSName in act.filesysNames:
                filename = "%s/%s.tex" % (folder, actFSName)
                if not os.path.isfile(filename):
                    print("geen details voor %s" % filename)
                    continue

                with open(filename, "r") as detailsfile:
                    print("openen van details voor %s" % filename)
                    for line in detailsfile:
                        actcontent += line
            if actcontent != "":
                result += "\\subsection{%s}" % act.name
                result += actcontent

        return result
