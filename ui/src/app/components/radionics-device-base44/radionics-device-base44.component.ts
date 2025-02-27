import { Component, ElementRef, ViewChild, AfterViewInit } from '@angular/core';

@Component({
  selector: 'app-radionics-device-base44',
  templateUrl: './radionics-device-base44.component.html',
  styleUrls: ['./radionics-device-base44.component.scss']
})
export class RadionicsDeviceBase44Component implements AfterViewInit {
  @ViewChild('rateDisplay', { static: false }) rateDisplay!: ElementRef;
  @ViewChild('targetInput', { static: false }) targetInput!: ElementRef;
  @ViewChild('powerBtn', { static: false }) powerBtn!: ElementRef;
  @ViewChild('broadcastContainer', { static: false }) broadcastContainer!: ElementRef;
  @ViewChild('timerDisplay', { static: false }) timerDisplay!: ElementRef;
  @ViewChild('frequencyMode', { static: false }) frequencyMode!: ElementRef;
  @ViewChild('frequencyPower', { static: false }) frequencyPower!: ElementRef;

  knobs: NodeListOf<Element> = document.querySelectorAll('.knob');
  inputs: NodeListOf<HTMLInputElement> = document.querySelectorAll('.knob-value');

  isPowered = false;
  startTime: number | null = null;
  timerInterval: any = null;
  broadcastInterval: any = null;

  ngAfterViewInit() {
    this.knobs = document.querySelectorAll('.knob');
    this.inputs = document.querySelectorAll('.knob-value');
    this.setupKnobs();
    this.setupEventListeners();
  }

  setupEventListeners(): void {
    this.frequencyPower.nativeElement.addEventListener('input', () => this.validateFrequencyPower());
    this.frequencyMode.nativeElement.addEventListener('change', () => { if (this.isPowered) this.restartBroadcast(); });
    this.frequencyPower.nativeElement.addEventListener('change', () => { if (this.isPowered) this.restartBroadcast(); });
    this.powerBtn.nativeElement.addEventListener('click', () => this.togglePower());
  }

  async restartBroadcast(): Promise<void> {
    clearInterval(this.broadcastInterval);
    await this.startBroadcast();
  }

  getRandomInt(max: number): number {
    const array = new Uint32Array(1);
    crypto.getRandomValues(array);
    return array[0] % max;
  }

  shuffleArray<T>(array: T[]): T[] {
    const shuffled = [...array];
    for (let i = shuffled.length - 1; i > 0; i--) {
      const j = this.getRandomInt(i + 1);
      [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    return shuffled;
  }

  shuffleHash(hash: string): string {
    return this.shuffleArray(hash.split('')).join('');
  }

  shuffleRate(rateString: string): string {
    if (!rateString) return '';
    return this.shuffleArray(rateString.split(' ').filter(val => val !== '')).join(' ');
  }

  setupKnobs(): void {
    this.knobs.forEach(knob => {
      const notchesContainer = knob.querySelector('.notches');
      console.log(notchesContainer);
      const pointer = knob.querySelector('.knob-pointer') as HTMLElement;

      for (let i = 0; i <= 44; i++) {
        const isMajor = i % 4 === 0;
        const rotation = this.calculateRotation(i);

        const notch = document.createElement('div');
        notch.className = `notch ${isMajor ? 'major' : ''}`;
        notch.style.transform = `rotate(${rotation}deg)`;
        notchesContainer?.appendChild(notch);
      }

      if (pointer) {
        pointer.style.transform = `translateX(-50%) rotate(${this.calculateRotation(0)}deg)`;
      }
    });
  }

  validateFrequencyPower(): number {
    let value = parseInt(this.frequencyPower.nativeElement.value, 10);
    if (isNaN(value) || value < 1) value = 1;
    if (value > 1000000) value = 1000000;
    this.frequencyPower.nativeElement.value = value;
    return value;
  }

  async generateSHA512(text: string): Promise<string> {
    const msgBuffer = new TextEncoder().encode(text);
    const hashBuffer = await crypto.subtle.digest('SHA-512', msgBuffer);
    return Array.from(new Uint8Array(hashBuffer))
      .map(b => b.toString(16).padStart(2, '0'))
      .join('');
  }

  async startBroadcast(): Promise<void> {
    const originalHash = await this.generateSHA512(this.targetInput.nativeElement.value);
    const frequency = this.calculateFrequency();
    const interval = Math.max(1, Math.floor(1000 / frequency));
    const potencyFactor = this.validateFrequencyPower();

    const shufflesPerInterval = Math.ceil(Math.log10(potencyFactor)) + 1;

    this.broadcastInterval = setInterval(async () => {
      for (let i = 0; i < shufflesPerInterval; i++) {
        console.log(`Broadcasting: ${this.shuffleRate(this.rateDisplay.nativeElement.textContent)} at ${frequency}Hz`);
        await new Promise(resolve => setTimeout(resolve, interval / shufflesPerInterval));
      }
    }, interval);
  }

  async togglePower(): Promise<void> {
    this.isPowered = !this.isPowered;

    if (this.isPowered) {
      this.powerBtn.nativeElement.textContent = 'Ausschalten';
      this.startTime = Date.now();
      this.timerInterval = setInterval(() => this.updateTimer(), 1000);
      this.broadcastContainer.nativeElement.style.display = 'block';
      await this.startBroadcast();
    } else {
      this.powerBtn.nativeElement.textContent = 'Einschalten';
      clearInterval(this.timerInterval);
      clearInterval(this.broadcastInterval);
      this.broadcastContainer.nativeElement.style.display = 'none';
    }
  }

  updateTimer(): void {
    if (!this.startTime) return;
    const elapsed = Math.floor((Date.now() - this.startTime) / 1000);
    const minutes = Math.floor(elapsed / 60);
    const seconds = elapsed % 60;
    this.timerDisplay.nativeElement.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
  }

  calculateFrequency(): number {
    return parseFloat(this.frequencyMode.nativeElement.value) * this.validateFrequencyPower();
  }

  calculateRotation(value: number): number {
    const totalRange = 285;
    const startAngle = 225;
    return (startAngle + (value / 44) * totalRange) % 360;
  }
}
