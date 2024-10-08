import {Component, OnInit} from '@angular/core';
import {Case} from "../../domains/Case";
import {FormControl} from "@angular/forms";

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {

  case:Case|undefined;

  constructor() {
  }

  ngOnInit(): void {
  }


}
