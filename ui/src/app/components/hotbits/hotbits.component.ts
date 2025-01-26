import {Component, OnInit} from '@angular/core';
import {AetherOneService} from "../../services/aether-one.service";
import {SocketService} from "../../services/socket.service";
import {ToastrService} from "ngx-toastr";

@Component({
  selector: 'app-hotbits',
  templateUrl: './hotbits.component.html',
  styleUrls: ['./hotbits.component.scss']
})
export class HotbitsComponent implements OnInit {

  settings:any
  hotbitsCount: number = 0
  webCamRunning: boolean = false

  constructor(private aetherOne: AetherOneService,
              private socketService: SocketService,
              private toastr: ToastrService) {
  }

  ngOnInit(): void {
    this.aetherOne.loadSettings().subscribe(s => {
      this.settings = s
    })
    this.countHotbits()
  }

  countHotbits() {
    this.aetherOne.countHotbits().subscribe( c => this.hotbitsCount = c.count)
    this.aetherOne.isWebCamHotRunning().subscribe( r => this.webCamRunning = r['running'])
    setTimeout(()=>{this.countHotbits()}, 10000)
  }

  startCollectingWebCamHotbits() {
    this.aetherOne.collectWebCamHotBits().subscribe(()=>{
      console.log("... collect hotbits from webcam ...")
    })
  }

  stopCollectingWebCamHotbits() {

  }
}
