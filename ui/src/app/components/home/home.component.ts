import {Component, OnInit} from '@angular/core'
import {Case} from "../../domains/Case"
import {FormControl} from "@angular/forms"
import {AetherOneService} from "../../services/aether-one.service";

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

  constructor(private aopyService:AetherOneService) {
  }

  ngOnInit(): void {
    this.aopyService.loadAllCases().subscribe( allCases => this.cases = allCases)
  }

  saveNewCase() {
    this.case = new Case()
    this.case.name = this.name?.value
    this.case.description = this.description?.value
    this.case.email = this.email?.value
    this.case.color = this.color?.value
    console.log(this.case)
    this.aopyService.saveNewCase(this.case).subscribe(c => this.case = c)
  }
}
