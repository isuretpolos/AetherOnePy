import {Injectable} from '@angular/core';
import {environment} from "../../environments/environment";
import {BehaviorSubject, Observable} from "rxjs";
import {HttpClient} from "@angular/common/http";
import {Case, Session} from "../domains/Case";
import {Analysis, Catalog, CountHotbits, RateObject} from "../domains/Analysis";
import {FolderStructure} from "../domains/Files";

@Injectable({
  providedIn: 'root'
})
export class AetherOneService {

  baseUrl: string = environment.baseUrl
  case$ = new BehaviorSubject<Case | undefined>(undefined);

  constructor(private http: HttpClient) {
  }

  ping(): Observable<any> {
    return this.http.get(`${this.baseUrl}ping`, {responseType: 'text'})
  }

  loadSettings(): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}settings`)
  }

  saveSettings(settings:any): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}settings`,settings)
  }

  saveNewCase(newCase: Case): Observable<Case> {
    return this.http.post<Case>(`${this.baseUrl}case`, newCase)
  }

  loadAllCases():Observable<Case[]> {
    return this.http.get<Case[]>(`${this.baseUrl}case`)
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
    return this.http.post<Analysis>(`${this.baseUrl}analysis`, analysis)
  }

  updateAnalysis(analysis:Analysis):Observable<Analysis> {
    return this.http.put<Analysis>(`${this.baseUrl}analysis`, analysis)
  }

  loadAnalysisList(session_id:number):Observable<Analysis[]> {
    return this.http.get<Analysis[]>(`${this.baseUrl}analysis?session_id=${session_id}`)
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
}
