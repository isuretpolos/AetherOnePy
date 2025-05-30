import {Component, OnInit} from '@angular/core'
import {Case} from "../../domains/Case"
import {FormControl} from "@angular/forms"
import {AetherOneService} from "../../services/aether-one.service";
import {Title} from "@angular/platform-browser";
import {ActivatedRoute, Router} from "@angular/router";
import {SqlSelect} from "../../domains/SqlSelect";
import {PlanetaryCalendar, PlanetaryInfo} from "../../domains/Planetary";
import {ToastrService} from "ngx-toastr";

@Component({
    selector: 'app-home',
    templateUrl: './home.component.html',
    styleUrls: ['./home.component.scss'],
    standalone: false
})
export class HomeComponent implements OnInit {

  case: Case | undefined;
  cases: Case[] = []
  name = new FormControl('', { nonNullable: true });
  email = new FormControl('', { nonNullable: true });
  color = new FormControl('', { nonNullable: true });
  description= new FormControl('', { nonNullable: true });
  averageRates:SqlSelect|undefined
  planetaryInfo:PlanetaryInfo|undefined
  planetaryCalendar:PlanetaryCalendar|undefined
  today = new Date().toISOString().split('T')[0]
  monthName = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'][new Date().getMonth()]

  constructor(
    private aetherOne:AetherOneService,
    private titleService: Title,
    private router: Router,
    private route: ActivatedRoute,
    private toastr: ToastrService) {
  }

  ngOnInit(): void {
    this.loadCases()

    this.aetherOne.sqlSelect(`SELECT signature, count(*) as counter FROM broadcast WHERE created > datetime('now','-21 days') GROUP BY signature ORDER BY counter DESC, signature LIMIT 10`).subscribe( a => {
      console.log(a)
      this.averageRates = a
    });

    this.aetherOne.planetaryInfo().subscribe( p => {
      this.planetaryInfo = p
      this.aetherOne.planetaryCalendar(new Date().getFullYear()).subscribe( c => this.planetaryCalendar = c)
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
    this.aetherOne.saveNewCase(this.case).subscribe( {next: c => {
      this.case = c
      this.titleService.setTitle(c.name)
      this.loadCases()
  }, error: e => this.toastr.error(e.error.message)})
  }

  selectCase(caseObj: Case) {
    this.titleService.setTitle(caseObj.name)
    sessionStorage.setItem('caseData', JSON.stringify(caseObj));
    this.router.navigate(['CASE']);
   }

  protected readonly length = length;

  resetNewCaseData() {
    this.name.setValue('')
    this.description.setValue('')
    this.email.setValue('')
    this.color.setValue('#000000')
  }
}
