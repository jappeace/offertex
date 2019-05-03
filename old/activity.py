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
    use_default = -1
    no_custom_details = ""
    def __init__(self):
        self.name = Activity.default_name
        self.setDuration(0)
        self.price_pp_euros = 0
        self.price_flat_euros = 0
        self.child_reduction_factor = 0.0
        self.custom_people_count = Activity.use_default
        self.custom_children_count = Activity.use_default
        self.directory = "" # to figure out the details
        self.detail_files =  []
        self.custom_details = Activity.no_custom_details # temporary custom details

    def __str__(self):
        result = self.name
        return result
    def __repr__(self):
        return self.name

    @staticmethod
    def create_from_file(filename, directory):
        """Make an activity from a json file"""
        result = Activity()
        result.directory = directory
        with open(filename,'r') as data:
            son = "".join(data.readlines())

            try:
                obj = json.loads(son)
            except ValueError as e:
                print("a json error occured with file: %s/%s" % (directory, filename))
                print(e)
                input()
                raise e
            for key in result.__dict__.keys():
                if key in obj:
                    if key == "duration_minutes":
                        result.setDuration(obj[key])
                        continue
                    result.__dict__[key] = obj[key]
            if result.name == Activity.default_name:
                result.name = filename.replace(".json", "").replace("_", " ")

            return result
        raise ValueError("Could not open %s" % filename)
    def ask_custom_people_count(self):
        """Promt user to modify the people count"""
        self.custom_people_count = inputs.intput(
            "Hoeveel mensen? %i voor gebruik groepgrote" % Activity.use_default
        )
    def ask_custom_children_count(self):
        """Promt user to modify the children count"""
        self.custom_children_count = inputs.intput(
            "Hoeveel mensen? %i voor gebruik groepgrote" % Activity.use_default
        )
    def setDuration(self, durationInMinutes):
        """Make sure duration is set in the propper manner"""
        self.duration_minutes = datetime.timedelta(minutes = durationInMinutes)

class ActivityManager:

    folder = "activities"
    def readdefaults():
        with open("default.json", "r") as deffile:
            return "".join(deffile.readlines())
        raise ValueError("couldn't read defaults")
    def createFromFileSystem():
        result = ActivityManager()
        os.chdir(ActivityManager.folder)

        reg = re.compile("\.json$")
        for directory in [d for d in os.listdir() if os.path.isdir(d)]:
            cat_key = directory.split('_',1)[-1].title().replace('_', ' ')
            os.chdir(directory)
            result.possible_activities[cat_key] = [
                Activity.create_from_file(fi, directory)
                for fi in os.listdir()
                if reg.search(fi) and os.path.isfile(fi)
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
    def planning(self, start_time):
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
            result.setDuration(inputs.intput("Hoe lang duurt %s in minuten?" % result.name))
            result.price_pp_euros = inputs.intput_float("Prijs per persoon, in euros")
            result.price_flat_euros = inputs.intput_float("Prijs, extra, ongeacht persoon aantal, in euros")
            if result.price_pp_euros != 0:
                result.child_reduction_factor = 1-inputs.intput_float("Kinder korting, in procenten") / 100
            result.ask_custom_people_count()
            self.current_activities.append(result)
        def edit_peoplecount():
            choice = inputs.userChoice("Which activity", self.current_activities)
            choice.ask_custom_people_count()
        def edit_childrencount():
            choice = inputs.userChoice("Which activity", self.current_activities)
            choice.ask_custom_children_count()
        def edit_duration():
            choice = inputs.userChoice("Which activity", self.current_activities)
            choice.setDuration(inputs.intput("hoelang %s in minuten?" % choice.name))
        def edit_custom_details():
            choice = inputs.userChoice("Which activity", self.current_activities)
            choice.custom_details = inputs.intput_str("Details in latex")
        special_operations = {
            " Verwijder laatste toevoeging": lambda: self.current_activities.pop(),
            " Klaar met planning en ga verder": disable_loop,
            " Voeg eigen veld toe": own_field,
            " Bewerk aantal personen van veld": edit_peoplecount,
            " Bewerk aantal kinderen van veld": edit_childrencount,
            " Bewerk duratie van veld": edit_duration,
            " Voeg details toe (extra gerechten kleine aanpassingen etc)": edit_custom_details
        }
        while run_menu_loop:
            self.printCurrentPlanning(start_time)
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
        go_back = " Terug"
        items.append(go_back)
        choice = inputs.userChoice("selecteer een %s activiteit" % category, items)
        if choice != go_back:
            self.current_activities.append(choice)

    def printCurrentPlanning(self, start_time):
        print("")
        print("---")
        def on_row(activity, time):
            timestring = time.strftime("%H:%M ")
            result = "%s %s" % (timestring, activity.name)
            if activity.custom_people_count != Activity.use_default:
                result += "\n       Aantal hoofden: %i" % activity.custom_people_count
            if activity.custom_details != Activity.no_custom_details:
                result += "\n       Extra details: %s" % activity.custom_details
            return result + "\n"

        if len(self.current_activities) > 0:
            print("Huidige planning:")
            reduction = reduce_with_time(self.current_activities, start_time, on_row)
            print(reduction.string)
            stub = Activity()
            stub.name = "Einde"
            print(on_row(stub, reduction.time))
        else:
            print("Geen planning")
        print("")

    def toTimeTableLatexStr(self, startingTime):
        result = "\\begin{tabular}{ll} \n"
        reduction = reduce_with_time(self.current_activities, startingTime,
                                     lambda a,t: t.strftime("%H.%M & " + str(a) + "\\\\\n")
        )
        result += reduction.string
        result += "%s & %s \\\\\n" % (reduction.time.strftime("%H.%M "), "Einde")
        result += "\n \\end{tabular} \n"
        return result

    def toPriceTableLatexStr(self, peopleCount, childrenCount):
        result = "\\begin{tabular}{l l l r l r} \n"
        totalPrice = 0
        childrenCount = int(childrenCount)
        peopleCount = int(peopleCount)

        for activity in self.current_activities:
            adults = peopleCount if activity.custom_people_count == Activity.use_default else activity.custom_people_count
            childs = childrenCount if activity.custom_children_count == Activity.use_default else activity.custom_children_count

            if childs != 0 and activity.child_reduction_factor != 0.0:
                adults -= childs

            if activity.price_pp_euros != 0:
                perPersonCosts = activity.price_pp_euros * adults
                totalPrice += perPersonCosts
                result += "%d & %s & \\euro{} & %.2f & \\euro{} & %.2f \\\\\n" % \
                (adults, activity, activity.price_pp_euros, perPersonCosts)

            if peopleCount != adults:
                # doulbe rounding is a big no no, but the offer should look
                # nice, and having individual cents on it just makes it look
                # greedy.
                # The only way to do this right is by doing double roundings
                # because we don't want people recalulating and have a difference
                # of several euros.
                childprice = round(activity.price_pp_euros * (1-activity.child_reduction_factor), 1)
                childCost = round(childs * childprice,1)
                result += "%d & Kinderen & \\euro{} & %.2f & \\euro{} & %.2f \\\\\n" % \
                (childs, childprice, childCost)
                totalPrice += childCost

            if activity.price_flat_euros != 0:
                result += "1 & %s & \\euro{} & %.2f & \\euro{} & %.2f \\\\\n" % \
                (activity, activity.price_flat_euros, activity.price_flat_euros)
                totalPrice += activity.price_flat_euros

        result += "\\hline\n"
        result += "& Totaal incl. btw & & & \\euro{} & %.2f \\\\\n" % totalPrice
        result += "\\end{tabular} \n"
        return result

    def activitiesDetailsText(self):
        result = ""
        print("starting figuring out details...")
        os.chdir(ActivityManager.folder)

        for act in self.current_activities:
            actcontent = act.custom_details
            if act.directory != "":
                os.chdir(act.directory)
            for detail in act.detail_files:
                filename = "%s.tex" % detail
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
            if act.directory != "":
                os.chdir("../")

        os.chdir("../")
        return result

from collections import namedtuple
ReductionResult = namedtuple("ReductionResult", ["string", "time"])
def reduce_with_time(current_activities, start_time, on_row_formater):
    currentTime = datetime.datetime.strptime(start_time, "%H:%M")
    result = ""
    for activity in current_activities:
        result += on_row_formater(activity, currentTime)
        currentTime += activity.duration_minutes
    return ReductionResult(result, currentTime)
