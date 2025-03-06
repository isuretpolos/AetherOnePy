export class PlanetaryInfo {
  month:Month
  day:Day
  hour:Hour
}

export class Month {
  month:string
  days:number
  currentDay:number
  planet:string
  zodiac:string
}

export class Day {
  day:string
  planet:string
}

export class Hour {
  hour:number
  planet:string
}
