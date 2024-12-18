import {Component, OnInit} from '@angular/core';
import {Case} from "../../domains/Case";
import {Router} from "@angular/router";
import {Catalog, RateObject} from "../../domains/Analysis";
import {AetherOneService} from "../../services/aether-one.service";
import {FolderStructure} from "../../domains/Files";

@Component({
  selector: 'app-case',
  templateUrl: './case.component.html',
  styleUrls: ['./case.component.scss']
})
export class CaseComponent implements OnInit {
  case:Case = new Case()
  catalogs:Catalog[] = []
  selectedCatalog:Catalog|undefined
  folderStructure: FolderStructure | null = null
  objectKeys = Object.keys;
  selectedFile: File | null = null;
  analysisResult:RateObject[] = []
  countHotbits:number = 0

  constructor(private aetherOne:AetherOneService) {}

  ngOnInit(): void {
    const storedData = sessionStorage.getItem('caseData');
    this.case = storedData ? JSON.parse(storedData) : null;
    this.aetherOne.countHotbits().subscribe( c => this.countHotbits = c.count)
  }

  loadRateCatalogs() {
    this.aetherOne.loadAllCatalogs().subscribe( c => this.catalogs = c)
  }

  loadFilesToImport() {
    this.aetherOne.loadAllFilesForImport().subscribe( f => this.folderStructure = f)
  }

  importFile(file: string) {
    this.aetherOne.importFileFromGithub(file).subscribe(f => {
      this.folderStructure = f
      this.loadRateCatalogs()
    })
  }

  async uploadFile(event: Event): Promise<void> {

    event.preventDefault();

    if (!this.selectedFile) {
      alert('Please select a file first!');
      return;
    }

    const formData = new FormData();
    formData.append('file', this.selectedFile);

    this.aetherOne.uploadFile(formData).subscribe({
      next: (response) => {
        console.log('Upload successful!', response)
        this.loadRateCatalogs()
      },
      error: (error) => console.error('Upload failed!', error),
    })
  }

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files?.length) {
      this.selectedFile = input.files[0];
    }
  }

  analyze() {
    if (this.selectedCatalog)
      this.aetherOne.analyze(this.selectedCatalog?.id).subscribe( r => {
        this.analysisResult = r
        this.aetherOne.countHotbits().subscribe( c => this.countHotbits = c.count)
      })
  }
}
