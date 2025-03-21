import {Component, OnInit} from '@angular/core';
import {FormControl} from "@angular/forms";
import {environment} from "../../../environments/environment";

@Component({
    selector: 'app-rate-cards',
    templateUrl: './rate-cards.component.html',
    styleUrls: ['./rate-cards.component.scss'],
    standalone: false
})
export class RateCardsComponent implements OnInit {

  rates= new FormControl('1 2 3', { nonNullable: true });
  rateName= new FormControl('Rate', { nonNullable: true });
  base= new FormControl('base10', { nonNullable: true });
  bases:string[] = ['base10','base44','base336']
  baseUrl: string = environment.baseUrl

  ngOnInit(): void {
  }

  getImageUrl(): string {
    return `${this.baseUrl}rateCard?rateName=${encodeURIComponent(this.rateName.getRawValue())}&rates=${encodeURIComponent(this.rates.getRawValue())}&base=${encodeURIComponent(this.base.getRawValue())}`;
  }
}
