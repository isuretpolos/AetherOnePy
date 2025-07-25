import {Injectable} from '@angular/core';
import {environment} from "../../environments/environment";
import {BehaviorSubject, Observable} from "rxjs";
import { HttpClient } from "@angular/common/http";
import {Case, Session} from "../domains/Case";
import {Analysis, Catalog, CountHotbits, RateObject} from "../domains/Analysis";
import {FolderStructure} from "../domains/Files";
import {BroadCastData} from "../domains/BroadCastData";
import {SqlSelect} from "../domains/SqlSelect";
import {PlanetaryCalendar, PlanetaryInfo} from "../domains/Planetary";

@Injectable({
  providedIn: 'root'
})
export class AetherOneService {

  baseUrl: string = environment.baseUrl
  case$ = new BehaviorSubject<Case | undefined>(undefined);

  constructor(private http: HttpClient) {
  }

  restart(): Observable<any> {
    return this.http.post(`${this.baseUrl}restart`, undefined)
  }

  shutdown(): Observable<any> {
    return this.http.post(`${this.baseUrl}shutdown`, undefined)
  }

  ping(): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}ping`)
  }

  cpuCount(): Observable<any> {
    return this.http.get(`${this.baseUrl}cpuCount`, {responseType: 'text'})
  }

  version(): Observable<any> {
    return this.http.get(`${this.baseUrl}version`, {responseType: 'text'})
  }

  remoteVersion(): Observable<any> {
    return this.http.get(`${this.baseUrl}remoteVersion`, {responseType: 'text'})
  }

  loadSettings(): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}settings`)
  }

  saveSettings(settings:any): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}settings`,settings)
  }

  loadPlugins(): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}plugins`)
  }

  saveNewCase(newCase: Case): Observable<Case> {
    return this.http.post<Case>(`${this.baseUrl}case`, newCase)
  }

  loadAllCases():Observable<Case[]> {
    return this.http.get<Case[]>(`${this.baseUrl}case`)
  }

  deleteCase(id:number):Observable<any> {
    return this.http.delete<any>(`${this.baseUrl}case?id=${id}`)
  }

  loadAllSessions(caseId:number):Observable<Session[]> {
    return this.http.get<Session[]>(`${this.baseUrl}session?caseId=${caseId}`)
  }

  newSession(session:Session):Observable<Session> {
    return this.http.post<Session>(`${this.baseUrl}session`, session)
  }

  loadSession(id: string):Observable<Session> {
    return this.http.get<Session>(`${this.baseUrl}session?id=${id}`)
  }

  loadLastSession(caseId: number):Observable<Session> {
    return this.http.get<Session>(`${this.baseUrl}session?caseId=${caseId}&last=true`)
  }

  deleteSession(id:number):Observable<any> {
    return this.http.delete<any>(`${this.baseUrl}session?id=${id}`)
  }


  loadAllCatalogs():Observable<Catalog[]> {
    return this.http.get<Catalog[]>(`${this.baseUrl}catalog`)
  }

  loadCatalog(id:number):Observable<Catalog> {
    return this.http.get<Catalog>(`${this.baseUrl}catalog?id=${id}`)
  }

  loadAllFilesForImport():Observable<FolderStructure> {
    return this.http.get<FolderStructure>(`${this.baseUrl}filesToImport`)
  }

  importFileFromGithub(fileName:string):Observable<FolderStructure> {
    return this.http.post<FolderStructure>(`${this.baseUrl}filesToImport?file=${fileName}`,undefined)
  }

  uploadFile(formData: any):Observable<any> {
    return this.http.post(`${this.baseUrl}upload`, formData)
  }

  newAnalysis(analysis:Analysis):Observable<Analysis> {
    console.log(analysis)
    return this.http.post<Analysis>(`${this.baseUrl}analysis`, analysis)
  }

  updateAnalysis(analysis:Analysis):Observable<Analysis> {
    return this.http.put<Analysis>(`${this.baseUrl}analysis`, analysis)
  }

  checkGeneralVitality(analysis:Analysis):Observable<any> {
    return this.http.post<any>(`${this.baseUrl}checkGV`, analysis)
  }

  loadAnalysisList(session_id:number):Observable<Analysis[]> {
    return this.http.get<Analysis[]>(`${this.baseUrl}analysis?session_id=${session_id}`)
  }

  loadLastAnalysis(session_id:number):Observable<Analysis> {
    return this.http.get<Analysis>(`${this.baseUrl}analysis?session_id=${session_id}&last=true`)
  }

  analyze(analysis_id:number,session_id:number, catalogId:number, note:string):Observable<RateObject[]> {
    return this.http.post<RateObject[]>(`${this.baseUrl}analyze`, {"analysis_id":analysis_id,"catalog_id":catalogId,"note":note, "session_id": session_id})
  }

  loadRatesForAnalysis(analysis_id:number):Observable<RateObject[]> {
    return this.http.get<RateObject[]>(`${this.baseUrl}analyze?analysis_id=${analysis_id}`)
  }

  countHotbits():Observable<CountHotbits> {
    return this.http.get<CountHotbits>(`${this.baseUrl}countHotbits`)
  }

  collectWebCamHotBits():Observable<any> {
    return this.http.post<any>(`${this.baseUrl}collectWebCamHotBits`,undefined)
  }

  openAiInterpretation(data:any):Observable<any> {
    return this.http.post<any>(`${this.baseUrl}openAiInterpretation`,data)
  }

  isWebCamHotRunning():Observable<any> {
    return this.http.get<any>(`${this.baseUrl}collectWebCamHotBits`)
  }

  stopCollectingHotbits():Observable<any> {
    return this.http.delete<any>(`${this.baseUrl}collectHotBits`)
  }

  broadcast(broadcastData:BroadCastData):Observable<any> {
    return this.http.post<any>(`${this.baseUrl}broadcast`,broadcastData)
  }

  getCurrentBroadcastTasks():Observable<any> {
    return this.http.get<any>(`${this.baseUrl}broadcast`)
  }

  stopAllBroadcasts():Observable<any> {
    return this.http.delete<any>(`${this.baseUrl}broadcast`)
  }

  planetaryInfo():Observable<PlanetaryInfo> {
    return this.http.get<PlanetaryInfo>(`${this.baseUrl}planetary_info`)
  }

  planetaryCalendar(year:number):Observable<PlanetaryCalendar> {
    return this.http.get<PlanetaryCalendar>(`${this.baseUrl}planetary_calendar/${year}`)
  }

  sqlSelect(sql:string):Observable<SqlSelect> {
    return this.http.post<SqlSelect>(`${this.baseUrl}sqlSelect`, {"sql":sql})
  }
}
