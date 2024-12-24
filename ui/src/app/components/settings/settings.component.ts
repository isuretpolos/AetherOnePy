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
  hotbits_collectAutomatically = new FormControl(false);
  hotbits_mix_TRNG = new FormControl(false);
  hotbits_use_Arduino = new FormControl(false);
  hotbits_use_ESP = new FormControl(false);
  hotbits_use_RPi = new FormControl(false);
  hotbits_use_WebCam = new FormControl(false);

  constructor(private aetherOne:AetherOneService) {
  }
  ngOnInit(): void {
    this.loadSettings()
  }

  loadSettings() {
    this.aetherOne.loadSettings().subscribe(s => {
      this.settings = s
      this.setBooleanValueForForm(this.analysisAdvanced,s['analysisAdvanced'])
      this.setBooleanValueForForm(this.hotbits_collectAutomatically,s['hotbits_collectAutomatically'])
      this.setBooleanValueForForm(this.hotbits_mix_TRNG,s['hotbits_mix_TRNG'])
      this.setBooleanValueForForm(this.hotbits_use_Arduino,s['hotbits_use_Arduino'])
      this.setBooleanValueForForm(this.hotbits_use_ESP,s['hotbits_use_ESP'])
      this.setBooleanValueForForm(this.hotbits_use_RPi,s['hotbits_use_RPi'])
      this.setBooleanValueForForm(this.hotbits_use_WebCam,s['hotbits_use_WebCam'])
    })
  }

  saveSettings() {

  }

  setBooleanValueForForm(formControl:FormControl, setting:string) {
      if ('true' == this.settings['analysisAdvanced'])
        this.analysisAdvanced.setValue(true);
      else
        this.analysisAdvanced.setValue(false);
  }

}
