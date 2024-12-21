export class Analysis {
  id:string = ""
  rateObjects:RateObject[] = []
  generalVitality:number = 0
}

export class RateObject {
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
