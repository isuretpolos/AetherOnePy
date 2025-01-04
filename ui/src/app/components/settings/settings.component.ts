import {Component, OnInit} from '@angular/core';
import {AetherOneService} from "../../services/aether-one.service";
import {FormControl} from "@angular/forms";

@Component({
  selector: 'app-settings',
  templateUrl: './settings.component.html',
  styleUrls: ['./settings.component.scss']
})
export class SettingsComponent implements OnInit {

  settings:any
  analysisAdvanced = new FormControl(false);
  analysisAlwaysCheckGV = new FormControl(false);
  hotbits_collectAutomatically = new FormControl(false);
  hotbits_mix_TRNG = new FormControl(false);
  hotbits_use_Arduino = new FormControl(false);
  hotbits_use_ESP = new FormControl(false);
  hotbits_use_RPi = new FormControl(false);
  hotbits_use_WebCam = new FormControl(false);
  hotbits_use_time_based_trng = new FormControl(true);
  savedSuccessShow:boolean = false

  constructor(private aetherOne:AetherOneService) {
  }
  ngOnInit(): void {
    this.loadSettings()
  }

  loadSettings() {
    this.aetherOne.loadSettings().subscribe(s => {
      this.settings = s
      this.analysisAdvanced.setValue(s['analysisAdvanced'])
      this.analysisAlwaysCheckGV.setValue(s['analysisAlwaysCheckGV'])
      this.hotbits_collectAutomatically.setValue(s['hotbits_collectAutomatically'])
      this.hotbits_mix_TRNG.setValue(s['hotbits_mix_TRNG'])
      this.hotbits_use_Arduino.setValue(s['hotbits_use_Arduino'])
      this.hotbits_use_ESP.setValue(s['hotbits_use_ESP'])
      this.hotbits_use_RPi.setValue(s['hotbits_use_RPi'])
      this.hotbits_use_WebCam.setValue(s['hotbits_use_WebCam'])
    })
  }

  saveSettings() {
    this.settings['analysisAdvanced'] = this.analysisAdvanced.getRawValue()
    this.settings['analysisAlwaysCheckGV'] = this.analysisAlwaysCheckGV.getRawValue()
    this.settings['hotbits_collectAutomatically'] = this.hotbits_collectAutomatically.getRawValue()
    this.settings['hotbits_mix_TRNG'] = this.hotbits_mix_TRNG.getRawValue()
    this.settings['hotbits_use_Arduino'] = this.hotbits_use_Arduino.getRawValue()
    this.settings['hotbits_use_ESP'] = this.hotbits_use_ESP.getRawValue()
    this.settings['hotbits_use_RPi'] = this.hotbits_use_RPi.getRawValue()
    this.settings['hotbits_use_WebCam'] = this.hotbits_use_WebCam.getRawValue()

    this.aetherOne.saveSettings(this.settings).subscribe(()=> {
      this.savedSuccessShow = true
      setTimeout(()=>{ this.savedSuccessShow = false }, 3000)
    })
  }

  setBooleanValueForForm(formControl:FormControl, setting:string) {
      if ('true' == this.settings['analysisAdvanced'])
        this.analysisAdvanced.setValue(true);
      else
        this.analysisAdvanced.setValue(false);
  }

}
