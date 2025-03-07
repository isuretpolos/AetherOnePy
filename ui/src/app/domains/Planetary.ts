export class PlanetaryInfo {
  season:Season
  month:Month
  day:Day
  hour:Hour
}

export class PlanetaryCalendar {
  season:Season
  months:Month[]
}

export class Month {
  month:string
  days_array:Day[]
  days_count:number
  currentDay:number
  planet:string
  zodiac:string
}

export class Day {
  day:string
  planet:string
  date:string
}

export class Hour {
  hour:number
  planet:string
}

export class Season {
  season:string
  dominantPlanets:string
  duration_days:number
  progress:number
  element:string
  end:string
  start:string
}