import {Component, OnInit} from '@angular/core';
import {AetherOneService} from "../../services/aether-one.service";
import {FormControl} from "@angular/forms";

@Component({
    selector: 'app-settings',
    templateUrl: './settings.component.html',
    styleUrls: ['./settings.component.scss'],
    standalone: false
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
  hotbits_use_time_based_trng = new FormControl(true)
  openAiSystemContent = new FormControl('')
  openAiUserContent = new FormControl('')
  openAiKey = new FormControl('')
  gpioRED = new FormControl(26);
  gpioBLUE = new FormControl(26);
  gpioGREEN = new FormControl(26);
  gpioLASER = new FormControl(26);
  gpioUV = new FormControl(26);
  gpioWHITE = new FormControl(26);
  useGPIOforBroadcasting = new FormControl(false);
  savedSuccessShow:boolean = false

  constructor(private aetherOne:AetherOneService) {
  }
  ngOnInit(): void {
    this.loadSettings()
    this.aetherOne.systemInfo().subscribe( i => console.log(i))
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
      this.hotbits_use_time_based_trng.setValue(s['hotbits_use_time_based_trng'])
      this.openAiSystemContent.setValue(s['openAiSystemContent'])
      this.openAiUserContent.setValue(s['openAiUserContent'])
      this.openAiKey.setValue(s['openAiKey'])
      this.gpioRED.setValue(s['gpioRED'])
      this.gpioBLUE.setValue(s['gpioBLUE'])
      this.gpioGREEN.setValue(s['gpioGREEN'])
      this.gpioLASER.setValue(s['gpioLASER'])
      this.gpioUV.setValue(s['gpioUV'])
      this.gpioWHITE.setValue(s['gpioWHITE'])
      this.useGPIOforBroadcasting.setValue(s['useGPIOforBroadcasting'])
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
    this.settings['hotbits_use_time_based_trng'] = this.hotbits_use_time_based_trng.getRawValue()
    this.settings['openAiSystemContent'] = this.openAiSystemContent.getRawValue()
    this.settings['openAiUserContent'] = this.openAiUserContent.getRawValue()
    this.settings['openAiKey'] = this.openAiKey.getRawValue()
    this.settings['gpioRED'] = this.gpioRED.getRawValue()
    this.settings['gpioBLUE'] = this.gpioBLUE.getRawValue()
    this.settings['gpioGREEN'] = this.gpioGREEN.getRawValue()
    this.settings['gpioLASER'] = this.gpioLASER.getRawValue()
    this.settings['gpioUV'] = this.gpioUV.getRawValue()
    this.settings['gpioWHITE'] = this.gpioWHITE.getRawValue()
    this.settings['useGPIOforBroadcasting'] = this.useGPIOforBroadcasting.getRawValue()

    this.aetherOne.saveSettings(this.settings).subscribe(()=> {
      this.savedSuccessShow = true
      setTimeout(()=>{ this.savedSuccessShow = false }, 3000)
    })
  }


}
