import {Component, OnInit} from '@angular/core';
import {Case} from "../../domains/Case";
import {Router} from "@angular/router";
import {Catalog} from "../../domains/Analysis";
import {AetherOneService} from "../../services/aether-one.service";

@Component({
  selector: 'app-case',
  templateUrl: './case.component.html',
  styleUrls: ['./case.component.scss']
})
export class CaseComponent implements OnInit {
  case:Case = new Case()
  catalogs:Catalog[] = []
  selectedCatalog:Catalog|undefined

  constructor(private aetherOne:AetherOneService) {}

  ngOnInit(): void {
    const storedData = sessionStorage.getItem('caseData');
    this.case = storedData ? JSON.parse(storedData) : null;
  }

  loadRateCatalogs() {
    this.aetherOne.loadAllCatalogs().subscribe( c => this.catalogs = c)
  }
}
