import { Component, ViewChild, ElementRef, AfterViewInit, OnDestroy } from '@angular/core';
import {FormBuilder, FormGroup, ReactiveFormsModule} from '@angular/forms';
import { Subject, takeUntil, debounceTime } from 'rxjs';
import {NgIf} from "@angular/common";

interface PotentiometerConfig {
  resolution: number;
  useAlpha: boolean;
  dialType: string;
  scaleStart: number;
  scaleEnd: number;
  divisions: number;
  startPosition: string;
  angleRange: number;
  bgColor: string;
  scaleColor: string;
  textColor: string;
  accentColor: string;
  scaleWidth: number;
  fontSize: number;
  showNumbers: boolean;
  showMinorTicks: boolean;
  showCenter: boolean;
  showLabel: boolean;
  labelText: string;
}

@Component({
  selector: 'app-potentiometer-generator',
  templateUrl: './potentiometer-sticker-generator.component.html',
  imports: [ReactiveFormsModule, NgIf],
  styleUrls: ['./potentiometer-sticker-generator.component.scss'],
})
export class PotentiometerStickerGeneratorComponent implements AfterViewInit, OnDestroy {

  @ViewChild('canvas', { static: true }) canvasRef!: ElementRef<HTMLCanvasElement>;

  configForm: FormGroup;
  private destroy$ = new Subject<void>();
  private ctx!: CanvasRenderingContext2D;

  constructor(private fb: FormBuilder) {
    this.configForm = this.fb.group({
      resolution: [1024],
      useAlpha: [false],
      dialType: ['rotary'],
      scaleStart: [0],
      scaleEnd: [10],
      divisions: [10],
      startPosition: ['right'],
      angleRange: [270],
      bgColor: ['#2c3e50'],
      scaleColor: ['#ecf0f1'],
      textColor: ['#ecf0f1'],
      accentColor: ['#e74c3c'],
      scaleWidth: [3],
      fontSize: [16],
      showNumbers: [true],
      showMinorTicks: [true],
      showCenter: [true],
      showLabel: [false],
      labelText: ['']
    });
  }

  ngAfterViewInit() {
    this.ctx = this.canvasRef.nativeElement.getContext('2d')!;
    this.setupFormSubscriptions();
    setTimeout(() => this.updatePreview(), 0);
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }

  private setupFormSubscriptions() {
    // Listen to form changes with debounce for smooth performance
    this.configForm.valueChanges
      .pipe(
        takeUntil(this.destroy$),
        debounceTime(50)
      )
      .subscribe(() => {
        this.updatePreview();
      });

    // Handle dial type presets
    this.configForm.get('dialType')?.valueChanges
      .pipe(takeUntil(this.destroy$))
      .subscribe(type => {
        this.applyDialTypePresets(type);
      });
  }

  private applyDialTypePresets(type: string) {
    const presets: { [key: string]: Partial<PotentiometerConfig> } = {
      frequency: {
        scaleStart: 0,
        scaleEnd: 10000,
        divisions: 11,
        labelText: 'FREQ',
        startPosition: 'bottom'
      },
      volume: {
        scaleStart: 0,
        scaleEnd: 10,
        divisions: 11,
        labelText: 'VOL',
        startPosition: 'bottom'
      },
      linear: {
        angleRange: 180,
        scaleStart: 0,
        scaleEnd: 100,
        divisions: 11,
        startPosition: 'bottom'
      },
      rotary: {
        angleRange: 270,
        scaleStart: 0,
        scaleEnd: 10,
        divisions: 11,
        startPosition: 'bottom'
      }
    };

    const preset = presets[type];
    if (preset) {
      this.configForm.patchValue(preset, { emitEvent: false });
      setTimeout(() => this.updatePreview(), 0);
    }
  }

  private updatePreview() {
    console.log("updatePreview called");
    this.drawPotentiometerSticker(this.canvasRef.nativeElement, 1, false);
  }

  private drawPotentiometerSticker(targetCanvas: HTMLCanvasElement, scale: number = 1, useAlpha: boolean = false) {
    const ctx = targetCanvas.getContext('2d')!;
    const size = targetCanvas.width;
    const center = size / 2;
    const radius = center * 0.8;
    const config = this.configForm.value as PotentiometerConfig;

    // Clear canvas - only fill background if not using alpha
    if (!useAlpha) {
      ctx.fillStyle = config.bgColor;
      ctx.fillRect(0, 0, size, size);
    } else {
      ctx.clearRect(0, 0, size, size);
    }

    ctx.save();

    const scaleWidth = config.scaleWidth * scale;
    const fontSize = config.fontSize * scale;

    // Calculate start angle based on position
    let startAngle: number;
    switch (config.startPosition) {
      case 'bottom':
        startAngle = 270 - config.angleRange / 2;
        break;
      case 'top':
        startAngle = 90 - config.angleRange / 2;
        break;
      case 'left':
        startAngle = 180 - config.angleRange / 2;
        break;
      case 'right':
      default:
        startAngle = 0 - config.angleRange / 2;
        break;
    }

    // Normalize angle to 0-360 range
    while (startAngle < 0) startAngle += 360;
    while (startAngle >= 360) startAngle -= 360;

    const angleStep = config.angleRange / (config.divisions - 1);

    // Draw major tick marks and numbers
    ctx.strokeStyle = config.scaleColor;
    ctx.lineWidth = scaleWidth;
    ctx.fillStyle = config.textColor;
    ctx.font = `bold ${fontSize}px Arial`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';

    for (let i = 0; i < config.divisions; i++) {
      const currentAngle = startAngle + i * angleStep;
      const angle = (currentAngle - 90) * Math.PI / 180;
      const value = Math.round((config.scaleStart + (config.scaleEnd - config.scaleStart) * i / (config.divisions - 1)) * 100) / 100;

      // Major tick mark
      const tickStart = radius * 0.85;
      const tickEnd = radius * 0.95;
      const x1 = center + tickStart * Math.cos(angle);
      const y1 = center + tickStart * Math.sin(angle);
      const x2 = center + tickEnd * Math.cos(angle);
      const y2 = center + tickEnd * Math.sin(angle);

      ctx.beginPath();
      ctx.moveTo(x1, y1);
      ctx.lineTo(x2, y2);
      ctx.stroke();

      // Numbers
      if (config.showNumbers) {
        const textRadius = radius * 0.75;
        const textX = center + textRadius * Math.cos(angle);
        const textY = center + textRadius * Math.sin(angle);

        let displayValue: string;
        if (config.dialType === 'frequency') {
          if (value >= 1000) {
            displayValue = (value / 1000).toFixed(1) + 'K';
          } else {
            displayValue = Math.round(value).toString();
          }
        } else {
          displayValue = value % 1 === 0 ? Math.round(value).toString() : value.toFixed(1);
        }

        ctx.fillText(displayValue, textX, textY);
      }
    }

    // Draw minor tick marks
    if (config.showMinorTicks) {
      ctx.lineWidth = scaleWidth * 0.5;
      const minorTicksPerMajor = 4;
      const totalMinorTicks = (config.divisions - 1) * minorTicksPerMajor;
      const minorAngleStep = config.angleRange / totalMinorTicks;

      for (let i = 0; i <= totalMinorTicks; i++) {
        if (i % minorTicksPerMajor !== 0) {
          const currentAngle = startAngle + i * minorAngleStep;
          const angle = (currentAngle - 90) * Math.PI / 180;
          const tickStart = radius * 0.9;
          const tickEnd = radius * 0.95;
          const x1 = center + tickStart * Math.cos(angle);
          const y1 = center + tickStart * Math.sin(angle);
          const x2 = center + tickEnd * Math.cos(angle);
          const y2 = center + tickEnd * Math.sin(angle);

          ctx.beginPath();
          ctx.moveTo(x1, y1);
          ctx.lineTo(x2, y2);
          ctx.stroke();
        }
      }
    }

    // Draw center dot
    if (config.showCenter) {
      ctx.fillStyle = config.accentColor;
      ctx.beginPath();
      ctx.arc(center, center, 4 * scale, 0, 2 * Math.PI);
      ctx.fill();
    }

    // Draw custom label
    if (config.showLabel && config.labelText.trim()) {
      ctx.fillStyle = config.textColor;
      ctx.font = `bold ${fontSize * 0.8}px Arial`;
      ctx.fillText(config.labelText.trim(), center, center + radius * 0.5);
    }

    // Draw outer ring
    ctx.strokeStyle = config.scaleColor;
    ctx.lineWidth = scaleWidth * 0.5;
    ctx.beginPath();
    ctx.arc(center, center, radius, 0, 2 * Math.PI);
    ctx.stroke();

    ctx.restore();
  }

  downloadHighRes() {
    try {
      const config = this.configForm.value as PotentiometerConfig;
      const highResCanvas = document.createElement('canvas');
      highResCanvas.width = config.resolution;
      highResCanvas.height = config.resolution;

      const scale = config.resolution / 400;
      this.drawPotentiometerSticker(highResCanvas, scale, config.useAlpha);

      setTimeout(() => {
        try {
          const link = document.createElement('a');
          const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
          const alphaText = config.useAlpha ? '_alpha' : '';
          link.download = `potentiometer_sticker_${config.resolution}x${config.resolution}${alphaText}_${timestamp}.png`;
          link.href = highResCanvas.toDataURL('image/png', 1.0);

          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);

          console.log('Download initiated successfully', config.useAlpha ? 'with alpha channel' : 'with solid background');
        } catch (error) {
          console.error('Error creating download link:', error);
          alert('Error creating download. Please try again.');
        }
      }, 100);

    } catch (error) {
      console.error('Error in downloadHighRes:', error);
      alert('Download failed. Please check console for details.');
    }
  }
}
