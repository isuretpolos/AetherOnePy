import {Component, OnInit} from '@angular/core';
import {Case, Session} from "../../domains/Case";
import {BroadCastData} from "../../domains/BroadCastData";
import {Analysis, Catalog, RateObject} from "../../domains/Analysis";
import {AetherOneService} from "../../services/aether-one.service";
import {FolderStructure} from "../../domains/Files";
import {FormControl} from "@angular/forms";
import {SqlSelect} from "../../domains/SqlSelect";

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
  broadcastResult:SqlSelect|undefined
  averageRates:SqlSelect|undefined

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

        this.aetherOne.sqlSelect(`SELECT signature, count(*) as counter FROM broadcast WHERE session_id = ${this.session.id} and created > datetime('now','-21 days') GROUP BY signature ORDER BY counter DESC, signature LIMIT 10`).subscribe( a => {
          this.averageRates = a
        });

        this.aetherOne.loadLastAnalysis(this.session.id).subscribe( a => {
          this.analysis = a
          this.aetherOne.loadCatalog(a.catalogId).subscribe( c => {
            this.selectedCatalog = c
            this.aetherOne.loadRatesForAnalysis(a.id).subscribe(rates => {
              this.analysisResult = rates
              this.checkHitGv()
            })
          })
        })

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
      analysis.catalogId = this.selectedCatalog.id

      this.aetherOne.newAnalysis(analysis).subscribe(persistedAnalysis => {
        this.analysis = persistedAnalysis
        this.aetherOne.analyze(this.analysis.id, this.session.id, this.selectedCatalog.id, this.analyzeNote.getRawValue()).subscribe(r => {
          this.analysisResult = r
          this.checkHitGv()
          this.aetherOne.countHotbits().subscribe(c => this.countHotbits = c.count)
        })
      })
    }
  }

  checkHitGv() {
    // find the highest gv from the analysis result
    this.analysis.hit_gv = this.analysisResult.reduce((max, p) => p.gv > max ? p.gv : max, 0)
    this.analysis.lowest_gv = this.analysisResult.reduce((min, p) => p.gv < min ? p.gv : min, 1000)
    this.analysis.highest_gv = this.analysis.target_gv
    if (this.analysis.hit_gv > this.analysis.highest_gv) {
      this.analysis.highest_gv = this.analysis.hit_gv
    }
    // calculate the percentage of the target gv that was hit
    // the percentage of target, hit and lowest gv should be 100% in the sum, in order to represent them in a bootstrap progress bar
    const total_gv = this.analysis.highest_gv;
    this.analysis.lowest_gv_percent = (this.analysis.lowest_gv / total_gv) * 100;
    this.analysis.target_gv_percent = (this.analysis.target_gv / total_gv) * 100;
    this.analysis.hit_gv_percent = (this.analysis.hit_gv / total_gv) * 100;
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

  getRateClass(target_gv: number, gv: number) {
    let rateClass = ''
    if (gv > target_gv) {
      rateClass = 'hitOverTarget'
    }
    if (gv > target_gv && gv >= 1000) {
      rateClass = 'hit1000'
    }
    return rateClass
  }

  broadcast(rate: RateObject) {
    let broadcastData = new BroadCastData(rate, this.analysis)
    this.aetherOne.broadcast(broadcastData).subscribe( r => console.log(r))
  }

  broadcastAll() {
    this.analysisResult.forEach( rate => {

      if (rate.gv >= this.analysis.target_gv) {
        let broadcastData = new BroadCastData(rate, this.analysis)
        this.aetherOne.broadcast(broadcastData).subscribe( r => console.log(r))
      }

    })
  }

  fetchBroadcastResult() {
    this.aetherOne.sqlSelect(`SELECT signature, repeat, leaving_with_general_vitality, created FROM broadcast WHERE analysis_id = ${this.analysis.id}`).subscribe(r => {
      console.log(r)
      this.broadcastResult = r
    })
  }

  stopAllBroadcasts() {
    console.log("try to stop")
    this.aetherOne.stopAllBroadcasts().subscribe( ()=> console.log("broadcasts stopped"))
  }
}
