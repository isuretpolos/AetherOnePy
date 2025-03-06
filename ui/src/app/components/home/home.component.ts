import {Component, OnInit} from '@angular/core'
import {Case} from "../../domains/Case"
import {FormControl} from "@angular/forms"
import {AetherOneService} from "../../services/aether-one.service";
import {Title} from "@angular/platform-browser";
import {ActivatedRoute, Router} from "@angular/router";
import {SqlSelect} from "../../domains/SqlSelect";

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {

  case: Case | undefined;
  cases: Case[] = []
  name = new FormControl('', { nonNullable: true });
  email = new FormControl('', { nonNullable: true });
  color = new FormControl('', { nonNullable: true });
  description= new FormControl('', { nonNullable: true });
  averageRates:SqlSelect|undefined
  planetaryInfo:any
  planetaryCalendar:any

  constructor(
    private aetherOne:AetherOneService,
    private titleService: Title,
    private router: Router,
    private route: ActivatedRoute,) {
  }

  ngOnInit(): void {
    this.loadCases()

    this.aetherOne.sqlSelect(`SELECT signature, count(*) as counter FROM broadcast WHERE created > datetime('now','-21 days') GROUP BY signature ORDER BY counter DESC, signature LIMIT 10`).subscribe( a => {
      this.averageRates = a
    });

    this.aetherOne.planetaryInfo().subscribe( p => {
      this.planetaryInfo = p
      this.aetherOne.planetaryCalendar(new Date().getFullYear()).subscribe( c => this.planetaryInfo = c)
    })

  }

  loadCases(): void {
    this.aetherOne.loadAllCases().subscribe( allCases => this.cases = allCases)
  }

  saveNewCase() {
    this.case = new Case()
    this.case.name = this.name?.value
    this.case.description = this.description?.value
    this.case.email = this.email?.value
    this.case.color = this.color?.value
    console.log(this.case)
    this.aetherOne.saveNewCase(this.case).subscribe(c => {
      this.case = c
      this.titleService.setTitle(c.name)
      this.loadCases()
  })
  }

  selectCase(caseObj: Case) {
    this.titleService.setTitle(caseObj.name)
    sessionStorage.setItem('caseData', JSON.stringify(caseObj));
    this.router.navigate(['CASE']);
   }
}
