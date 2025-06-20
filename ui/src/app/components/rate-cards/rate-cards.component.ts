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

  rates = new FormControl('1 2 3', {nonNullable: true});
  rateName = new FormControl('Rate', {nonNullable: true});
  base = new FormControl('base10', {nonNullable: true});
  bases: string[] = ['base10', 'base44', 'base336']
  baseUrl: string = environment.baseUrl

  ngOnInit(): void {
  }

  getImageUrl(): string {
    return `${this.baseUrl}rateCard?rateName=${encodeURIComponent(this.rateName.getRawValue())}&rates=${encodeURIComponent(this.rates.getRawValue())}&base=${encodeURIComponent(this.base.getRawValue())}`;
  }

  generateRate() {
    let codes = this.generateRateCodes(this.rateName.getRawValue())
    if (this.base.getRawValue() === 'base10') {
      this.rates.setValue(codes.base10.join(' '))
    }
    if (this.base.getRawValue() === 'base44') {
      this.rates.setValue(codes.base44.join(' '))
    }
    if (this.base.getRawValue() === 'base336') {
      this.rates.setValue(codes.base336.join(' '))
    }
  }

  generateRateCodes(input: string): {
    base10: number[],
    base44: number[],
    base336: number[]
  } {
    const cleaned = input.replace(/[^A-Za-z0-9]/g, '').toUpperCase();

    const charMap: { [key: string]: number } = {};
    const alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    for (let i = 0; i < alphabet.length; i++) {
      charMap[alphabet[i]] = i;
    }

    const chunkValues = (base: number): number[] => {
      const result: number[] = [];
      for (let i = 0; i < 4; i++) {
        const c1 = charMap[cleaned[i * 2]] ?? 0;
        const c2 = charMap[cleaned[i * 2 + 1]] ?? 0;
        result.push(c1 * base + c2);
      }
      return result;
    };

    return {
      base10: chunkValues(10),
      base44: chunkValues(44),
      base336: chunkValues(336)
    };
  }
}
