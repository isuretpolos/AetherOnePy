import {Analysis, RateObject} from "./Analysis";

export class Case {
  id:number = 0
  name:string = ""
  email:string = ""
  color:string = "" // hex value
  description: string = ""
  created:Date = new Date()
  lastChange:Date = new Date()
}

export class Session {
  id:number = 0
  caseID:number = 0
  intention:string = ""
  description:string = ""
  created:Date = new Date()
}


export class RateObjectWrapper {
  occurrence:number = 0
  overallEnergeticValue:number = 0
  overallGV:number = 0
  rateObject:RateObject = new RateObject()
  name:string = ""
}

export class MapDesign {
  id:number = 0
  caseID:number = 0
  uuid:string = ""
  coordinatesX:number = 0
  coordinatesY:number = 0
  zoom:number = 10
}

export class Feature {
  id:number = 0
  mapID:number = 0
  territoryName:string = ""
  simpleFeatureData:string = ""
  simpleFeatureType:string = ""
  note:string = ""
  url:string = ""
  lastUpdate:Date = new Date()
}
