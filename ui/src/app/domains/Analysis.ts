export class Analysis {
  id:number = 0
  sessionID:number = 0
  note:string = ""
  catalogId:number = -1
  rateObjects:RateObject[] = []
  target_gv:number = 0
  hit_gv:number = 0
  highest_gv:number = 0
  lowest_gv:number = 0
  highest_gv_percent:number = 0
  lowest_gv_percent:number = 0
  target_gv_percent:number = 0
  hit_gv_percent:number = 0
}

export class RateObject {
  id:number = 0
  signature:string = ""
  url:string = ""
  gv:number = 0
  energetic_value:number = 0
  recurring:number = 0
  recurringGeneralVitality:number = 0
  level:number = 0
  potency:string = ""
  resonateCounter:number = 0
}

export class Catalog {
  id:number = 0
  name:string = ""
  description:string = ""
  author:string = ""
  importdate:Date = new Date()
}

export class GV {
  gv:number = -1
}

export class CountHotbits {
  count:number = 0
}
