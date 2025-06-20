import {Analysis, RateObject} from "./Analysis";

export class BroadCastData {
  id: number;
  rate_id: number = 0;
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
  target: string|undefined;
  level: string|undefined;
  potency: string|undefined;


  constructor(private rate: RateObject|undefined = undefined, analysis: Analysis|undefined = undefined) {
    if (rate) {
      this.rate_id = rate.id
      this.signature = rate.signature;
    }
    if (analysis) {
      this.analysis_id = analysis.id;
      this.sessionID = analysis.sessionID;
    }

    this.entering_with_general_vitality = 0;
    this.leaving_with_general_vitality = 0;
  }
}
