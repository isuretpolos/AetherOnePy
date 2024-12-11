import {Component, OnInit} from '@angular/core';
import {Case} from "../../domains/Case";
import {Router} from "@angular/router";

@Component({
  selector: 'app-case',
  templateUrl: './case.component.html',
  styleUrls: ['./case.component.scss']
})
export class CaseComponent implements OnInit {
  case:Case = new Case()

  constructor(private router: Router) {}

  ngOnInit(): void {
    const storedData = sessionStorage.getItem('caseData');
    this.case = storedData ? JSON.parse(storedData) : null;
  }
}
