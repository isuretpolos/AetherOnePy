import sys,os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from datetime import datetime, timedelta
from py.domains.planetaryDomains import PlanetaryInfo

# Define planetary rulerships
zodiac_monthly = {
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
}

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
        for season, (element, planets, (start_month, start_day), (end_month, end_day)) in seasonal_rulerships.items():
            start = datetime(date.year, start_month, start_day)
            end = datetime(date.year, end_month, end_day)
            if start <= date <= end:
                total_days = (end - start).days
                progress = round(((date - start).days / total_days) * 100, 1)
                return {"season": season, "progress": f"{progress}%", "element": element, "dominantPlanet": planets}
        return {}


    def planetary_info(self)->PlanetaryInfo:
        now = datetime.now()
        month_name = now.strftime("%B")
        day_name = now.strftime("%A")
        season_data = self.get_season(now)
        zodiac = next((z for z in zodiac_monthly if z[0] == month_name), None)
        weekday = now.weekday()
        first_hour_ruler = daily_rulerships[list(daily_rulerships)[weekday]]
        index = planetary_hours.index(first_hour_ruler)

        data = PlanetaryInfo()
        data.month.month = month_name
        data.month.days = (datetime(now.year, now.month % 12 + 1, 1) - datetime(now.year, now.month, 1)).days
        data.month.zodiac = zodiac[1]
        data.month.planet = zodiac[2]
        data.day.day = day_name
        data.day.planet = daily_rulerships[day_name]
        data.hour.hour = now.hour
        data.hour.planet = planetary_hours[(index + now.hour) % 7]

        return data

    def generate_calendar(self, year):
        calendar_data = {"year": year, "months": [], "seasons": {}}

        for season, (element, planets, (start_month, start_day), (end_month, end_day)) in seasonal_rulerships.items():
            start_date = datetime(year, start_month, start_day)
            end_date = datetime(year, end_month, end_day)
            total_days = (end_date - start_date).days
            calendar_data["seasons"][season] = {
                "start": start_date.strftime("%Y-%m-%d"),
                "end": end_date.strftime("%Y-%m-%d"),
                "element": element,
                "dominantPlanets": planets,
                "duration_days": total_days
            }

        for i, (month, zodiac, ruling_planet) in enumerate(zodiac_monthly):
            first_day = datetime(year, i + 1, 1)

            if i == 11:  # December case: wrap around to next year
                last_day = datetime(year + 1, 1, 1) - timedelta(days=1)
            else:
                last_day = datetime(year, i + 2, 1) - timedelta(days=1)

            days_in_month = (last_day - first_day).days + 1

            month_data = {
                "month": month,
                "days": days_in_month,
                "zodiac": zodiac,
                "rulingPlanet": ruling_planet,
                "days_data": {}
            }

            for day in range(1, days_in_month + 1):
                date = datetime(year, first_day.month, day)
                weekday = date.strftime("%A")
                month_data["days_data"][day] = {
                    "date": date.strftime("%Y-%m-%d"),
                    "weekday": weekday,
                    "rulingPlanet": daily_rulerships[weekday]
                }

            calendar_data["months"].append(month_data)

        return calendar_data