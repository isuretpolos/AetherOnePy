import { Component, OnInit } from '@angular/core';
import { AetherOneService } from 'src/app/services/aether-one.service';

@Component({
    selector: 'app-version',
    templateUrl: './version.component.html',
    styleUrls: ['./version.component.scss'],
    standalone: false
})
export class VersionComponent implements OnInit {

  version: string = ''
  remoteVersion: string = ''

  constructor(private aetherOne: AetherOneService) {}

  ngOnInit(): void {
    this.aetherOne.version().subscribe(v => this.version = v)
    this.aetherOne.remoteVersion().subscribe(v => this.remoteVersion = v)
  }

  restart() {
    this.aetherOne.restart().subscribe()
  }
}
