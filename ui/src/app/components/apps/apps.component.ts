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

  constructor(private aether:AetherOneService, private toast:ToastrService) { }

  ngOnInit(): void {
    this.apps.push(
      {name: 'Radionics Device Base 44', route: 'RADIONICS_DEVICE_BASE44', image: 'assets/images/radionicsDeviceBased44.jpg', description: 'Base 44 Radionics Device based on Benjamin Ludwig\'s design'},
      {name: 'Radionics Cards', route: 'CARDS', image: 'assets/images/radionicsCards.png', description: 'Make radionics cards'},
    );
    this.aether.loadPlugins().subscribe({"next": (data) => {
      this.plugins = data.plugins;
    }, "error": (err) => {this.toast.error("Error loading plugins: " + err.message, "Error", {timeOut: 5000})} })
  }
}
