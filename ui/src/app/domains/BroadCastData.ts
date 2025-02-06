import {Analysis, RateObject} from "./Analysis";

export class BroadCastData {
  id: number;
  clear: boolean = false;
  intention: string = '';
  signature: string = '';
  delay: number = 0;
  repeat: number = 1;
  analysis_id: number = 0;
  entering_with_general_vitality: number = 0;
  leaving_with_general_vitality: number = 0;
  sessionID: number = 0;
  created: Date = new Date();

  constructor(rate: RateObject, analysis: Analysis) {
    this.signature = rate.signature;
    this.analysis_id = analysis.id;
    this.entering_with_general_vitality = 0;
    this.leaving_with_general_vitality = 0;
    this.sessionID = analysis.sessionID;
  }
}
