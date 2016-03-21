
class Activity:
    def __init__(self, naam, duratie, prijs):
        self.naam = naam
        self.duratie = duratie
        self.prijs = prijs

class ActivityDecoration(Activity):
    def __init(self, decoratingActivity, withActivity):
        self.decorating = decoratingActivity
        self.withActivity = withActivity
