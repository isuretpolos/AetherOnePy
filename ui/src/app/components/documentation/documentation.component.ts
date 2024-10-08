import {Component, OnInit} from '@angular/core';
import {AetherOneService} from "../../services/aether-one.service";

@Component({
  selector: 'app-documentation',
  templateUrl: './documentation.component.html',
  styleUrls: ['./documentation.component.scss']
})
export class DocumentationComponent implements OnInit {

  qrCodeUrl: string = "http://localhost/qrcode";

  constructor(private aetherOne:AetherOneService) {
  }

  ngOnInit(): void {
  }


}
