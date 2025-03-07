

class PlanetaryInfo:
    def __init__(self):
        self.season = Season()
        self.month = Month()
        self.day = Day()
        self.hour = Hour()

    def to_dict(self):
        return {
            "season": self.season.to_dict(),
            "month": self.month.to_dict(),
            "day": self.day.to_dict(),
            "hour": self.hour.to_dict(),
        }
    
class PlanetaryCalendar:
    def __init__(self):
        self.months = []
        self.seasons = []
    
    def to_dict(self):

        return {
            "months": [month.to_dict() for month in self.months],
            "seasons": [season.to_dict() for season in self.seasons],
        }

class Season:
    def __init__(self):
        self.season = ''
        self.dominantPlanets = ''
        self.duration_days = 1
        self.progress = 0
        self.element = ''
        self.start = ''
        self.end = ''

    def to_dict(self):
        return {
            "season": self.season,
            "dominantPlanets": self.dominantPlanets,
            "duration_days": self.duration_days,
            "progress": self.progress,
            "element": self.element,
            "start": self.start,
            "end": self.end,
        }


class Month:
    def __init__(self):
        self.month = ''
        self.days_count = 1
        self.days_array = []
        self.currentDay = 1
        self.planet = ''
        self.zodiac = ''

    def to_dict(self):

        days = [day.to_dict() for day in self.days_array]

        return {
            "month": self.month,
            "days_array": days,
            "days_count": self.days_count,
            "currentDay": self.currentDay,
            "planet": self.planet,
            "zodiac": self.zodiac,
        }


class Day:
    def __init__(self):
        self.day = ''
        self.planet = ''
        self.date = ''

    def to_dict(self):
        return {
            "day": self.day,
            "planet": self.planet,
            "date": self.date
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
