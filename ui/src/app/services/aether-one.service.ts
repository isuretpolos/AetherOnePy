import {Injectable} from '@angular/core';
import {environment} from "../../environments/environment";
import {BehaviorSubject, Observable} from "rxjs";
import {HttpClient} from "@angular/common/http";
import {Case} from "../domains/Case";
import {Catalog, CountHotbits, RateObject} from "../domains/Analysis";
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

  saveNewCase(newCase: Case): Observable<Case> {
    return this.http.post<Case>(`${this.baseUrl}case`, newCase);
  }

  loadAllCases():Observable<Case[]> {
    return this.http.get<Case[]>(`${this.baseUrl}case`)
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
    return this.http.post(`${this.baseUrl}upload`, formData);
  }

  analyze(catalogId:number):Observable<RateObject[]> {
    return this.http.post<RateObject[]>(`${this.baseUrl}analyze`, {"catalog_id":catalogId});
  }

  countHotbits():Observable<CountHotbits> {
    return this.http.get<CountHotbits>(`${this.baseUrl}countHotbits`)
  }
}
