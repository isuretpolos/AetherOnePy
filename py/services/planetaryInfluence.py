import sys,os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from datetime import datetime, timedelta
from domains.planetaryDomains import PlanetaryInfo, PlanetaryCalendar, Season, Month, Day

# Define planetary rulerships
zodiac_monthly = [
    ("January", "Capricorn", "Saturn"),
    ("February", "Aquarius", "Uranus"),
    ("March", "Pisces", "Neptune"),
    ("April", "Aries", "Mars"),
    ("May", "Taurus", "Venus"),
    ("June", "Gemini", "Mercury"),
    ("July", "Cancer", "Moon"),
    ("August", "Leo", "Sun"),
    ("September", "Virgo", "Mercury"),
    ("October", "Libra", "Venus"),
    ("November", "Scorpio", "Pluto"),
    ("December", "Sagittarius", "Jupiter")
]

daily_rulerships = {
    "Monday": "Moon",
    "Tuesday": "Mars",
    "Wednesday": "Mercury",
    "Thursday": "Jupiter",
    "Friday": "Venus",
    "Saturday": "Saturn",
    "Sunday": "Sun"
}

seasonal_rulerships = {
    "Spring": ("Fire", "Mars, Sun", (3, 20), (6, 20)),
    "Summer": ("Water", "Moon, Venus", (6, 21), (9, 21)),
    "Autumn": ("Air", "Mercury, Saturn", (9, 22), (12, 20)),
    "Winter": ("Earth", "Saturn, Jupiter", (12, 21), (3, 19))
}

planetary_hours = ["Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter", "Mars"]

class PlanetaryRulershipCalendarAPI:

    def __init__(self):
        pass

    def get_season(self, date):

        season_data = Season()

        for season, (element, planets, (start_month, start_day), (end_month, end_day)) in seasonal_rulerships.items():
            print(season)
            start = datetime(date.year, start_month, start_day)
            end = datetime(date.year, end_month, end_day)
            if start <= date <= end:
                total_days = (end - start).days
                season_data.season = season
                season_data.element = element
                season_data.dominantPlanets = planets
                season_data.start = start.strftime("%Y-%m-%d")
                season_data.end = end.strftime("%Y-%m-%d")
                season_data.duration_days = total_days
                season_data.progress = round(((date - start).days / total_days) * 100, 1)
                print(season_data)
                break
        return season_data


    def planetary_info(self)->PlanetaryInfo:
        now = datetime.now()
        month_name = now.strftime("%B")
        day_name = now.strftime("%A")
        zodiac = next((z for z in zodiac_monthly if z[0] == month_name), None)
        weekday = now.weekday()

        data = PlanetaryInfo()
        data.season = self.get_season(now)
        data.month.month = month_name
        data.month.days_count = (datetime(now.year, now.month % 12 + 1, 1) - datetime(now.year, now.month, 1)).days
        data.month.zodiac = zodiac[1]
        data.month.planet = zodiac[2]
        data.day.day = day_name
        data.day.planet = daily_rulerships[day_name]
        data.hour.hour = now.hour

        first_hour_ruler = daily_rulerships[list(daily_rulerships)[weekday]]
        index = planetary_hours.index(first_hour_ruler)
        data.hour.planet = planetary_hours[(index + now.hour) % 7]

        return data

    def generate_calendar(self, year):
        calendar_data = PlanetaryCalendar()

        for season, (element, planets, (start_month, start_day), (end_month, end_day)) in seasonal_rulerships.items():
            start_date = datetime(year, start_month, start_day)
            end_date = datetime(year, end_month, end_day)
            total_days = (end_date - start_date).days
            season_data = Season()
            season_data.season = season
            season_data.element = element
            season_data.dominantPlanets = planets
            season_data.start = start_date.strftime("%Y-%m-%d")
            season_data.end = end_date.strftime("%Y-%m-%d")
            season_data.duration_days = total_days
            calendar_data.seasons.append(season_data)


        i = 0
        for month, zodiac, ruling_planet in zodiac_monthly:
            first_day = datetime(year, i + 1, 1)

            if i == 11:  # December case: wrap around to next year
                last_day = datetime(year + 1, 1, 1) - timedelta(days=1)
            else:
                last_day = datetime(year, i + 2, 1) - timedelta(days=1)

            days_in_month = (last_day - first_day).days + 1

            month_data = Month()
            month_data.month = month
            month_data.days_count = days_in_month
            month_data.zodiac = zodiac
            month_data.planet = ruling_planet

            for day in range(1, days_in_month + 1):
                date = datetime(year, first_day.month, day)
                weekday = date.strftime("%A")
                day_data = Day()
                day_data.date = date.strftime("%Y-%m-%d")
                day_data.day = weekday
                day_data.planet = daily_rulerships[weekday]
                month_data.days_array.append(day_data)

            calendar_data.months.append(month_data)
            i += 1  

        return calendar_data