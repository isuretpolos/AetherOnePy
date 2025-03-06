class PlanetaryInfo:
    def __init__(self):
        self.month = Month()
        self.day = Day()
        self.hour = Hour()

    def to_dict(self):
        return {
            "month": self.month.to_dict(),
            "day": self.day.to_dict(),
            "hour": self.hour.to_dict(),
        }


class Month:
    def __init__(self):
        self.month = ''
        self.days = 1
        self.currentDay = 1
        self.planet = ''
        self.zodiac = ''

    def to_dict(self):
        return {
            "month": self.month,
            "days": self.days,
            "currentDay": self.currentDay,
            "planet": self.planet,
            "zodiac": self.zodiac,
        }


class Day:
    def __init__(self):
        self.day = ''
        self.planet = ''

    def to_dict(self):
        return {
            "day": self.day,
            "planet": self.planet,
        }


class Hour:
    def __init__(self):
        self.hour = 1
        self.planet = ''

    def to_dict(self):
        return {
            "hour": self.hour,
            "planet": self.planet,
        }
