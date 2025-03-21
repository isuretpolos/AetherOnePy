import { Component , OnInit} from '@angular/core';

@Component({
    selector: 'app-apps',
    templateUrl: './apps.component.html',
    styleUrls: ['./apps.component.scss'],
    standalone: false
})
export class AppsComponent implements OnInit {

  apps = [];

  constructor() { }

  ngOnInit(): void {
    this.apps.push({name: 'Radionics Device Base 44', route: 'RADIONICS_DEVICE_BASE44', image: 'assets/images/radionicsDeviceBased44.jpg', description: 'Base 44 Radionics Device based on Benjamin Ludwig\'s design'});
  }
}
