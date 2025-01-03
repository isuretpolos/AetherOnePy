import {Component, OnInit} from '@angular/core';
import {Case, Session} from "../../domains/Case";
import {Router} from "@angular/router";
import {Analysis, Catalog, RateObject} from "../../domains/Analysis";
import {AetherOneService} from "../../services/aether-one.service";
import {FolderStructure} from "../../domains/Files";
import {FormControl} from "@angular/forms";

@Component({
  selector: 'app-case',
  templateUrl: './case.component.html',
  styleUrls: ['./case.component.scss']
})
export class CaseComponent implements OnInit {
  settings:any
  case:Case = new Case()
  sessions:Session[] = []
  session:Session|undefined
  analysis:Analysis|undefined
  analysisList:Analysis[] = []
  catalogs:Catalog[] = []
  selectedCatalog:Catalog|undefined
  folderStructure: FolderStructure | null = null
  objectKeys = Object.keys;
  selectedFile: File | null = null;
  analysisResult:RateObject[] = []
  countHotbits:number = 0
  sessionDescription= new FormControl('', { nonNullable: true });
  sessionIntention= new FormControl('', { nonNullable: true });
  analyzeNote= new FormControl('', { nonNullable: true });

  constructor(private aetherOne:AetherOneService) {}

  ngOnInit(): void {
    this.aetherOne.loadSettings().subscribe(s => this.settings = s )
    const storedData = sessionStorage.getItem('caseData');
    this.case = storedData ? JSON.parse(storedData) : null;
    if (this.case) {
      this.aetherOne.loadAllSessions(this.case.id).subscribe(sessions => this.sessions = sessions)
      this.aetherOne.loadLastSession(this.case.id).subscribe( s => {
        this.session = s
        this.sessionDescription.setValue(s.description)
        this.sessionIntention.setValue(s.intention)

        this.aetherOne.loadAnalysisList(this.session.id).subscribe( a => {
          this.analysisList = a
          this.analysisList.forEach( analysis => {
            this.aetherOne.loadRatesForAnalysis(analysis.id).subscribe(rates => analysis.rateObjects = rates)
          })
        })
      })
    }
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

    if (this.selectedCatalog && this.session) {
      let analysis = new Analysis()
      analysis.sessionID = this.session.id

      this.aetherOne.newAnalysis(analysis).subscribe(persistedAnalysis => {
        this.analysis = persistedAnalysis
        this.aetherOne.analyze(this.analysis.id, this.session.id, this.selectedCatalog.id, this.analyzeNote.getRawValue()).subscribe(r => {
          this.analysisResult = r
          this.aetherOne.countHotbits().subscribe(c => this.countHotbits = c.count)
        })
      })
    }
  }

  newSession() {
    this.session = new Session()
    this.session.caseID = this.case.id
    this.session.description = this.sessionDescription.getRawValue()
    this.session.intention = this.sessionIntention.getRawValue()

    this.aetherOne.newSession(this.session).subscribe( s => {
      this.session = s
      this.analysisList = []
      this.analysis = undefined
    })
  }

  deleteSession(id: number) {
    if(confirm("Are you sure you want to delete this session?")) {
      this.aetherOne.deleteSession(id).subscribe( ()=>{
        this.aetherOne.loadAllSessions(this.case.id).subscribe(sessions => this.sessions = sessions)
      })
    }
  }

  showSessionDetails(session: Session) {
    console.log("not yet implemented")
  }

  saveAnalysisNote() {
    this.analysis.note = this.analyzeNote.getRawValue()
    this.aetherOne.updateAnalysis(this.analysis).subscribe( a=> console.log(a))
  }

  resetSessionData() {
    this.sessionIntention.setValue("")
    this.sessionDescription.setValue("")
  }
}
