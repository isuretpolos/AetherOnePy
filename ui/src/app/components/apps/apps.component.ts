import { Component , OnInit} from '@angular/core';
import {AetherOneService} from "../../services/aether-one.service";
import {Toast, ToastrService} from "ngx-toastr";

@Component({
    selector: 'app-apps',
    templateUrl: './apps.component.html',
    styleUrls: ['./apps.component.scss'],
    standalone: false
})
export class AppsComponent implements OnInit {

  apps = []
  plugins = []
  iframeUrl:string|undefined
  pluginName:string|undefined

  constructor(private aether:AetherOneService, private toast:ToastrService) { }

  ngOnInit(): void {
    this.apps.push(
      {name: 'Radionics Device Base 44', route: 'RADIONICS_DEVICE_BASE44', image: 'assets/images/radionicsDeviceBased44.jpg', description: 'Base 44 Radionics Device based on Benjamin Ludwig\'s design'},
      {name: 'Radionics Cards', route: 'CARDS', image: 'assets/images/radionicsCards.png', description: 'Make radionics cards'},
      {name: 'Potentiometer Sticker Generator', route: 'POTENTIOMETER', image: 'assets/images/potentiometerGenerator.png', description: 'A fully interactive dial/sticker generator for potentiometer stickers, with live preview and high‑resolution export.'},
    );
    this.aether.loadPlugins().subscribe({"next": (data) => {
      this.plugins = data.plugins;
    }, "error": (err) => {this.toast.error("Error loading plugins: " + err.message, "Error", {timeOut: 5000})} })
  }

  openPluginModal(plugin: any) {
    this.iframeUrl = window.location.origin + '/' + plugin.ui
  }
}
